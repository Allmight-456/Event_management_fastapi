"""
Tests for event management endpoints.

This module tests event CRUD operations, versioning, and conflict detection.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.event import Event
from app.models.user import User


class TestEventCRUD:
    """Test basic event CRUD operations."""

    def test_create_event_success(self, client: TestClient, auth_headers: dict, sample_event_data: dict):
        """Test successful event creation."""
        response = client.post("/api/v1/events/", json=sample_event_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_event_data["title"]
        assert data["description"] == sample_event_data["description"]
        assert data["version"] == 1

    def test_create_event_unauthorized(self, client: TestClient, sample_event_data: dict):
        """Test event creation without authentication."""
        response = client.post("/api/v1/events/", json=sample_event_data)
        
        assert response.status_code == 401

    def test_create_event_invalid_time(self, client: TestClient, auth_headers: dict):
        """Test event creation with end time before start time."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time - timedelta(hours=1)  # End before start
        
        event_data = {
            "title": "Invalid Event",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "is_recurring": False,
            "recurrence_type": "none"
        }
        
        response = client.post("/api/v1/events/", json=event_data, headers=auth_headers)
        
        assert response.status_code == 422

    def test_create_event_conflict_detection(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test conflict detection when creating overlapping events."""
        # Create event that overlaps with test_event
        conflicting_event_data = {
            "title": "Conflicting Event",
            "start_time": test_event.start_time.isoformat(),
            "end_time": test_event.end_time.isoformat(),
            "is_recurring": False,
            "recurrence_type": "none"
        }
        
        response = client.post("/api/v1/events/", json=conflicting_event_data, headers=auth_headers)
        
        assert response.status_code == 409
        assert "conflicts" in response.json()["detail"].lower()

    def test_get_events_success(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting events list."""
        response = client.get("/api/v1/events/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test event
        event_ids = [event["id"] for event in data]
        assert test_event.id in event_ids

    def test_get_events_pagination(self, client: TestClient, auth_headers: dict):
        """Test events pagination."""
        response = client.get("/api/v1/events/?skip=0&limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_events_date_filter(self, client: TestClient, auth_headers: dict):
        """Test events filtering by date."""
        tomorrow = datetime.utcnow() + timedelta(days=1)
        response = client.get(
            f"/api/v1/events/?start_date={tomorrow.isoformat()}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200

    def test_get_event_by_id(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting specific event by ID."""
        response = client.get(f"/api/v1/events/{test_event.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_event.id
        assert data["title"] == test_event.title

    def test_get_event_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent event."""
        response = client.get("/api/v1/events/99999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_event_success(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test successful event update."""
        update_data = {
            "title": "Updated Event Title",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/v1/events/{test_event.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Event Title"
        assert data["description"] == "Updated description"
        assert data["version"] == 2  # Version should increment

    def test_update_event_unauthorized(self, client: TestClient, test_event: Event):
        """Test event update without authentication."""
        update_data = {"title": "Updated Title"}
        
        response = client.put(f"/api/v1/events/{test_event.id}", json=update_data)
        
        assert response.status_code == 401

    def test_delete_event_success(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test successful event deletion."""
        response = client.delete(f"/api/v1/events/{test_event.id}", headers=auth_headers)
        
        assert response.status_code == 204

    def test_delete_event_unauthorized(self, client: TestClient, test_event: Event):
        """Test event deletion without authentication."""
        response = client.delete(f"/api/v1/events/{test_event.id}")
        
        assert response.status_code == 401


class TestEventBatch:
    """Test batch event operations."""

    def test_create_batch_events_success(self, client: TestClient, auth_headers: dict):
        """Test successful batch event creation."""
        base_time = datetime.utcnow() + timedelta(days=1)
        
        batch_data = {
            "events": [
                {
                    "title": f"Batch Event {i}",
                    "start_time": (base_time + timedelta(hours=i*2)).isoformat(),
                    "end_time": (base_time + timedelta(hours=i*2+1)).isoformat(),
                    "is_recurring": False,
                    "recurrence_type": "none"
                }
                for i in range(3)
            ]
        }
        
        response = client.post("/api/v1/events/batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_create_batch_events_with_conflict(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test batch creation with conflicting events."""
        batch_data = {
            "events": [
                {
                    "title": "Good Event",
                    "start_time": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                    "end_time": (datetime.utcnow() + timedelta(days=2, hours=1)).isoformat(),
                    "is_recurring": False,
                    "recurrence_type": "none"
                },
                {
                    "title": "Conflicting Event",
                    "start_time": test_event.start_time.isoformat(),
                    "end_time": test_event.end_time.isoformat(),
                    "is_recurring": False,
                    "recurrence_type": "none"
                }
            ]
        }
        
        response = client.post("/api/v1/events/batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == 400  # Batch should fail completely


class TestEventVersioning:
    """Test event versioning and history features."""

    def test_get_event_history(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting event version history."""
        response = client.get(f"/api/v1/events/{test_event.id}/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "versions" in data
        assert len(data["versions"]) >= 1

    def test_get_specific_version(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting specific event version."""
        response = client.get(f"/api/v1/events/{test_event.id}/versions/1", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version_number"] == 1

    def test_get_version_not_found(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting non-existent version."""
        response = client.get(f"/api/v1/events/{test_event.id}/versions/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_rollback_event(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test event rollback functionality."""
        # First update the event to create version 2
        update_data = {"title": "Updated Title"}
        client.put(f"/api/v1/events/{test_event.id}", json=update_data, headers=auth_headers)
        
        # Now rollback to version 1
        response = client.post(f"/api/v1/events/{test_event.id}/rollback/1", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_event.title  # Should be back to original title

    def test_compare_versions(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test version comparison functionality."""
        # Update event to create version 2
        update_data = {"title": "Updated Title", "description": "New description"}
        client.put(f"/api/v1/events/{test_event.id}", json=update_data, headers=auth_headers)
        
        # Compare versions
        response = client.get(f"/api/v1/events/{test_event.id}/diff/1/2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "changes" in data
        assert "version1" in data
        assert "version2" in data

    def test_get_changelog(self, client: TestClient, auth_headers: dict, test_event: Event):
        """Test getting event changelog."""
        response = client.get(f"/api/v1/events/{test_event.id}/changelog", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "changelog" in data
        assert isinstance(data["changelog"], list)


class TestEventRecurrence:
    """Test recurring event functionality."""

    def test_create_recurring_event(self, client: TestClient, auth_headers: dict, recurring_event_data: dict):
        """Test creating recurring event."""
        response = client.post("/api/v1/events/", json=recurring_event_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_recurring"] == True
        assert data["recurrence_type"] == "daily"
        assert data["recurrence_pattern"] is not None
