"""
Integration tests for the Event Management API.

This module tests end-to-end workflows and complex scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.event import Event


class TestWorkflowIntegration:
    """Test complete workflows and user journeys."""

    def test_complete_event_lifecycle(self, client: TestClient, db_session: Session):
        """Test complete event lifecycle from creation to deletion."""
        # 1. Register a user
        user_data = {
            "username": "lifecycleuser",
            "email": "lifecycle@example.com",
            "password": "password123",
            "full_name": "Lifecycle User"
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        tokens = register_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # 2. Create an event
        start_time = datetime.utcnow() + timedelta(days=1)
        event_data = {
            "title": "Lifecycle Event",
            "description": "Testing complete lifecycle",
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "is_recurring": False,
            "recurrence_type": "none"
        }
        create_response = client.post("/api/v1/events/", json=event_data, headers=headers)
        assert create_response.status_code == 201
        event = create_response.json()
        event_id = event["id"]

        # 3. Update the event (creates version 2)
        update_data = {"title": "Updated Lifecycle Event"}
        update_response = client.put(f"/api/v1/events/{event_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        assert update_response.json()["version"] == 2

        # 4. Get event history
        history_response = client.get(f"/api/v1/events/{event_id}/history", headers=headers)
        assert history_response.status_code == 200
        assert len(history_response.json()["versions"]) == 2

        # 5. Compare versions
        diff_response = client.get(f"/api/v1/events/{event_id}/diff/1/2", headers=headers)
        assert diff_response.status_code == 200
        assert "changes" in diff_response.json()

        # 6. Rollback to version 1
        rollback_response = client.post(f"/api/v1/events/{event_id}/rollback/1", headers=headers)
        assert rollback_response.status_code == 200
        assert rollback_response.json()["title"] == "Lifecycle Event"

        # 7. Delete the event
        delete_response = client.delete(f"/api/v1/events/{event_id}", headers=headers)
        assert delete_response.status_code == 204

    def test_collaboration_workflow(self, client: TestClient, db_session: Session):
        """Test complete collaboration workflow."""
        # Create two users
        user1_data = {
            "username": "collab1",
            "email": "collab1@example.com",
            "password": "password123",
            "full_name": "Collaborator One"
        }
        user2_data = {
            "username": "collab2",
            "email": "collab2@example.com",
            "password": "password123",
            "full_name": "Collaborator Two"
        }

        # Register users
        user1_response = client.post("/api/v1/auth/register", json=user1_data)
        user2_response = client.post("/api/v1/auth/register", json=user2_data)
        
        user1_tokens = user1_response.json()
        user2_tokens = user2_response.json()
        
        user1_headers = {"Authorization": f"Bearer {user1_tokens['access_token']}"}
        user2_headers = {"Authorization": f"Bearer {user2_tokens['access_token']}"}

        # User 1 creates an event
        start_time = datetime.utcnow() + timedelta(days=1)
        event_data = {
            "title": "Collaboration Event",
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "is_recurring": False,
            "recurrence_type": "none"
        }
        create_response = client.post("/api/v1/events/", json=event_data, headers=user1_headers)
        event_id = create_response.json()["id"]

        # User 1 shares event with User 2 as editor
        share_data = {
            "users": [{"user_id": user2_tokens["user_id"], "permission_level": "editor"}]
        }
        share_response = client.post(f"/api/v1/events/{event_id}/share", json=share_data, headers=user1_headers)
        assert share_response.status_code == 201

        # User 2 can now view the event
        view_response = client.get(f"/api/v1/events/{event_id}", headers=user2_headers)
        assert view_response.status_code == 200

        # User 2 can edit the event
        edit_data = {"description": "Edited by collaborator"}
        edit_response = client.put(f"/api/v1/events/{event_id}", json=edit_data, headers=user2_headers)
        assert edit_response.status_code == 200

        # Check collaborators list
        collab_response = client.get(f"/api/v1/events/{event_id}/collaborators", headers=user1_headers)
        assert collab_response.status_code == 200
        assert collab_response.json()["total_collaborators"] == 2

    def test_batch_operations_workflow(self, client: TestClient, auth_headers: dict):
        """Test batch operations workflow."""
        base_time = datetime.utcnow() + timedelta(days=1)
        
        # Create batch of events
        batch_data = {
            "events": [
                {
                    "title": f"Batch Event {i}",
                    "start_time": (base_time + timedelta(hours=i*2)).isoformat(),
                    "end_time": (base_time + timedelta(hours=i*2+1)).isoformat(),
                    "is_recurring": False,
                    "recurrence_type": "none"
                }
                for i in range(5)
            ]
        }
        
        batch_response = client.post("/api/v1/events/batch", json=batch_data, headers=auth_headers)
        assert batch_response.status_code == 201
        events = batch_response.json()
        assert len(events) == 5

        # Verify all events were created
        list_response = client.get("/api/v1/events/", headers=auth_headers)
        event_titles = [event["title"] for event in list_response.json()]
        
        for i in range(5):
            assert f"Batch Event {i}" in event_titles

    def test_error_handling_workflow(self, client: TestClient):
        """Test error handling in various scenarios."""
        # Test authentication required
        response = client.get("/api/v1/events/")
        assert response.status_code == 401

        # Test invalid token
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/events/", headers=invalid_headers)
        assert response.status_code == 401

        # Test resource not found
        valid_user_data = {
            "username": "erroruser",
            "email": "error@example.com",
            "password": "password123",
            "full_name": "Error User"
        }
        register_response = client.post("/api/v1/auth/register", json=valid_user_data)
        tokens = register_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = client.get("/api/v1/events/99999", headers=headers)
        assert response.status_code == 404

    def test_concurrent_operations(self, client: TestClient, db_session: Session):
        """Test concurrent operations on the same event."""
        # Create user and event
        user_data = {
            "username": "concurrentuser",
            "email": "concurrent@example.com",
            "password": "password123",
            "full_name": "Concurrent User"
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)
        tokens = register_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Create event
        start_time = datetime.utcnow() + timedelta(days=1)
        event_data = {
            "title": "Concurrent Event",
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "is_recurring": False,
            "recurrence_type": "none"
        }
        create_response = client.post("/api/v1/events/", json=event_data, headers=headers)
        event_id = create_response.json()["id"]

        # Simulate concurrent updates
        update1_data = {"title": "Update 1"}
        update2_data = {"title": "Update 2"}

        response1 = client.put(f"/api/v1/events/{event_id}", json=update1_data, headers=headers)
        response2 = client.put(f"/api/v1/events/{event_id}", json=update2_data, headers=headers)

        # Both should succeed (last one wins)
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Check final state
        final_response = client.get(f"/api/v1/events/{event_id}", headers=headers)
        assert final_response.json()["title"] == "Update 2"


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_schema(self, client: TestClient):
        """Test OpenAPI schema endpoint."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "components" in schema

    def test_swagger_ui(self, client: TestClient):
        """Test Swagger UI endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc(self, client: TestClient):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_health_endpoints(self, client: TestClient):
        """Test health check endpoints."""
        # Root endpoint
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

        # Health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@pytest.mark.asyncio
class TestAsyncOperations:
    """Test asynchronous operations and concurrent requests."""

    async def test_async_event_creation(self, client: TestClient, auth_headers: dict):
        """Test asynchronous event creation."""
        import asyncio
        
        async def create_event(event_num):
            start_time = datetime.utcnow() + timedelta(days=1, hours=event_num)
            event_data = {
                "title": f"Async Event {event_num}",
                "start_time": start_time.isoformat(),
                "end_time": (start_time + timedelta(hours=1)).isoformat(),
                "is_recurring": False,
                "recurrence_type": "none"
            }
            
            response = client.post("/api/v1/events/", json=event_data, headers=auth_headers)
            return response.status_code

        # Create multiple events concurrently
        tasks = [create_event(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 201 for status in results)
