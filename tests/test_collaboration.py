"""
Tests for collaboration and permission management endpoints.

This module tests event sharing, permission management, and collaborative features.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.user import User
from app.models.permission import PermissionLevel


class TestEventSharing:
    """Test event sharing functionality."""

    def test_share_event_success(self, client: TestClient, auth_headers: dict, test_event: Event, test_user2: User):
        """Test successful event sharing."""
        share_data = {
            "users": [
                {
                    "user_id": test_user2.id,
                    "permission_level": "viewer"
                }
            ]
        }
        
        response = client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "shared_with" in data
        assert len(data["shared_with"]) == 1
        assert data["shared_with"][0]["user_id"] == test_user2.id
        assert data["shared_with"][0]["status"] == "granted"

    def test_share_event_multiple_users(self, client: TestClient, auth_headers: dict, test_event: Event, test_user2: User, test_admin: User):
        """Test sharing event with multiple users."""
        share_data = {
            "users": [
                {
                    "user_id": test_user2.id,
                    "permission_level": "viewer"
                },
                {
                    "user_id": test_admin.id,
                    "permission_level": "editor"
                }
            ]
        }
        
        response = client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["shared_with"]) == 2

    def test_share_event_nonexistent_user(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test sharing with non-existent user."""
        share_data = {
            "users": [
                {
                    "user_id": 99999,
                    "permission_level": "viewer"
                }
            ]
        }
        
        response = client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Users not found" in response.json()["detail"]

    def test_share_event_unauthorized(self, client: TestClient, test_event: Event, test_user2: User):
        """Test sharing without proper permissions."""
        # Create headers for test_user2 (not the owner)
        from app.core.security import create_access_token
        token_data = {"sub": test_user2.id, "username": test_user2.username, "role": test_user2.role.value}
        access_token = create_access_token(token_data)
        headers = {"Authorization": f"Bearer {access_token}"}
        
        share_data = {
            "users": [
                {
                    "user_id": test_user2.id,
                    "permission_level": "viewer"
                }
            ]
        }
        
        response = client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=headers)
        
        assert response.status_code == 403

    def test_share_nonexistent_event(self, client: TestClient, auth_headers: dict, test_user2: User):
        """Test sharing non-existent event."""
        share_data = {
            "users": [
                {
                    "user_id": test_user2.id,
                    "permission_level": "viewer"
                }
            ]
        }
        
        response = client.post("/api/v1/events/99999/share", json=share_data, headers=auth_headers)
        
        assert response.status_code == 404


class TestPermissionManagement:
    """Test permission management functionality."""

    def test_get_event_permissions(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting event permissions."""
        response = client.get(f"/api/v1/events/{test_event.id}/permissions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the owner
        
        # Owner should be first in the list
        owner_permission = data[0]
        assert owner_permission["user_id"] == test_event.owner_id
        assert owner_permission["permission_level"] == "owner"

    def test_update_user_permission(self, client: TestClient, auth_headers: dict, test_event: Event, test_user2: User):
        """Test updating user permission."""
        # First share the event
        share_data = {
            "users": [{"user_id": test_user2.id, "permission_level": "viewer"}]
        }
        client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        # Now update permission
        update_data = {"permission_level": "editor"}
        response = client.put(
            f"/api/v1/events/{test_event.id}/permissions/{test_user2.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["new_permission_level"] == "editor"

    def test_update_owner_permission_forbidden(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test that owner permissions cannot be modified."""
        update_data = {"permission_level": "viewer"}
        response = client.put(
            f"/api/v1/events/{test_event.id}/permissions/{test_event.owner_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Cannot modify owner's permissions" in response.json()["detail"]

    def test_revoke_user_permission(self, client: TestClient, auth_headers: dict, test_event: Event, test_user2: User):
        """Test revoking user permission."""
        # First share the event
        share_data = {
            "users": [{"user_id": test_user2.id, "permission_level": "viewer"}]
        }
        client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        # Now revoke permission
        response = client.delete(
            f"/api/v1/events/{test_event.id}/permissions/{test_user2.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "revoked successfully" in data["message"]

    def test_revoke_nonexistent_permission(self, client: TestClient, auth_headers: dict, test_event: Event, test_user2: User):
        """Test revoking non-existent permission."""
        response = client.delete(
            f"/api/v1/events/{test_event.id}/permissions/{test_user2.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_revoke_owner_permission_forbidden(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test that owner permissions cannot be revoked."""
        response = client.delete(
            f"/api/v1/events/{test_event.id}/permissions/{test_event.owner_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 400


class TestCollaborators:
    """Test collaborator management functionality."""

    def test_get_event_collaborators(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting event collaborators."""
        response = client.get(f"/api/v1/events/{test_event.id}/collaborators", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "collaborators" in data
        assert "total_collaborators" in data
        assert len(data["collaborators"]) >= 1  # At least the owner
        
        # Check owner is in collaborators
        owner_found = any(
            collab["user_id"] == test_event.owner_id and collab["role"] == "owner"
            for collab in data["collaborators"]
        )
        assert owner_found

    def test_get_collaborators_with_shared_users(self, client: TestClient, auth_headers: dict, test_event: Event, test_user2: User):
        """Test getting collaborators after sharing."""
        # Share event first
        share_data = {
            "users": [{"user_id": test_user2.id, "permission_level": "editor"}]
        }
        client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        # Get collaborators
        response = client.get(f"/api/v1/events/{test_event.id}/collaborators", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_collaborators"] == 2
        
        # Check both owner and shared user are present
        user_ids = [collab["user_id"] for collab in data["collaborators"]]
        assert test_event.owner_id in user_ids
        assert test_user2.id in user_ids

    def test_get_collaborators_unauthorized(self, client: TestClient, test_event: Event, test_user2: User):
        """Test getting collaborators without permission."""
        # Create headers for test_user2 (not the owner or collaborator)
        from app.core.security import create_access_token
        token_data = {"sub": test_user2.id, "username": test_user2.username, "role": test_user2.role.value}
        access_token = create_access_token(token_data)
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = client.get(f"/api/v1/events/{test_event.id}/collaborators", headers=headers)
        
        assert response.status_code == 403


class TestPermissionHierarchy:
    """Test permission hierarchy and access control."""

    def test_viewer_cannot_edit_event(self, client: TestClient, test_event: Event, test_user2: User, auth_headers: dict):
        """Test that viewers cannot edit events."""
        # Share event with viewer permission
        share_data = {
            "users": [{"user_id": test_user2.id, "permission_level": "viewer"}]
        }
        client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        # Try to edit as viewer
        from app.core.security import create_access_token
        token_data = {"sub": test_user2.id, "username": test_user2.username, "role": test_user2.role.value}
        access_token = create_access_token(token_data)
        viewer_headers = {"Authorization": f"Bearer {access_token}"}
        
        update_data = {"title": "Unauthorized Update"}
        response = client.put(
            f"/api/v1/events/{test_event.id}", 
            json=update_data, 
            headers=viewer_headers
        )
        
        assert response.status_code == 403

    def test_editor_can_edit_event(self, client: TestClient, test_event: Event, test_user2: User, auth_headers: dict):
        """Test that editors can edit events."""
        # Share event with editor permission
        share_data = {
            "users": [{"user_id": test_user2.id, "permission_level": "editor"}]
        }
        client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        # Try to edit as editor
        from app.core.security import create_access_token
        token_data = {"sub": test_user2.id, "username": test_user2.username, "role": test_user2.role.value}
        access_token = create_access_token(token_data)
        editor_headers = {"Authorization": f"Bearer {access_token}"}
        
        update_data = {"title": "Editor Update"}
        response = client.put(
            f"/api/v1/events/{test_event.id}", 
            json=update_data, 
            headers=editor_headers
        )
        
        assert response.status_code == 200

    def test_viewer_can_view_event(self, client: TestClient, test_event: Event, test_user2: User, auth_headers: dict):
        """Test that viewers can view events."""
        # Share event with viewer permission
        share_data = {
            "users": [{"user_id": test_user2.id, "permission_level": "viewer"}]
        }
        client.post(f"/api/v1/events/{test_event.id}/share", json=share_data, headers=auth_headers)
        
        # Try to view as viewer
        from app.core.security import create_access_token
        token_data = {"sub": test_user2.id, "username": test_user2.username, "role": test_user2.role.value}
        access_token = create_access_token(token_data)
        viewer_headers = {"Authorization": f"Bearer {access_token}"}
        
        response = client.get(f"/api/v1/events/{test_event.id}", headers=viewer_headers)
        
        assert response.status_code == 200
