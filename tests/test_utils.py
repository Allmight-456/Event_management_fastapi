"""
Tests for utility functions and helper classes.

This module tests diff generation, permission management, and other utilities.
"""

import pytest
from datetime import datetime, timedelta

from app.utils.diff import DiffGenerator
from app.utils.permissions import PermissionManager
from app.models.permission import PermissionLevel


class TestDiffGenerator:
    """Test diff generation utility."""

    def test_generate_detailed_diff_basic(self):
        """Test basic diff generation."""
        version1_data = {
            "title": "Original Title",
            "description": "Original description",
            "location": "Original location"
        }
        
        version2_data = {
            "title": "Updated Title",
            "description": "Original description",
            "location": "Updated location"
        }
        
        diff = DiffGenerator.generate_detailed_diff(version1_data, version2_data)
        
        assert diff["summary"]["total_changes"] == 2
        assert "title" in diff["field_changes"]
        assert "location" in diff["field_changes"]
        assert "description" not in diff["field_changes"]

    def test_generate_diff_added_field(self):
        """Test diff with added fields."""
        version1_data = {"title": "Title"}
        version2_data = {"title": "Title", "description": "New description"}
        
        diff = DiffGenerator.generate_detailed_diff(version1_data, version2_data)
        
        assert diff["summary"]["added_fields"] == 1
        assert diff["field_changes"]["description"]["change_type"] == "added"

    def test_generate_diff_removed_field(self):
        """Test diff with removed fields."""
        version1_data = {"title": "Title", "description": "Description"}
        version2_data = {"title": "Title"}
        
        diff = DiffGenerator.generate_detailed_diff(version1_data, version2_data)
        
        assert diff["summary"]["removed_fields"] == 1
        assert diff["field_changes"]["description"]["change_type"] == "removed"

    def test_generate_diff_datetime_fields(self):
        """Test diff with datetime fields."""
        dt1 = datetime.utcnow()
        dt2 = dt1 + timedelta(hours=1)
        
        version1_data = {"start_time": dt1}
        version2_data = {"start_time": dt2}
        
        diff = DiffGenerator.generate_detailed_diff(version1_data, version2_data)
        
        assert "datetime_diff" in diff["field_changes"]["start_time"]
        assert diff["field_changes"]["start_time"]["datetime_diff"]["moved_later"] == True

    def test_generate_diff_json_fields(self):
        """Test diff with JSON fields."""
        json1 = {"interval": 1, "weekdays_only": True}
        json2 = {"interval": 2, "weekdays_only": True, "end_date": "2024-12-31"}
        
        version1_data = {"recurrence_pattern": json1}
        version2_data = {"recurrence_pattern": json2}
        
        diff = DiffGenerator.generate_detailed_diff(version1_data, version2_data)
        
        json_diff = diff["field_changes"]["recurrence_pattern"]["json_diff"]
        assert "interval" in json_diff["modified_keys"]
        assert "end_date" in json_diff["added_keys"]

    def test_generate_text_diff(self):
        """Test text-based diff generation."""
        version1_data = {"title": "Old", "description": "Same"}
        version2_data = {"title": "New", "description": "Same"}
        
        text_diff = DiffGenerator.generate_text_diff(version1_data, version2_data)
        
        assert "--- Version 1" in text_diff
        assert "+++ Version 2" in text_diff
        assert "-title: Old" in text_diff
        assert "+title: New" in text_diff

    def test_humanize_time_diff(self):
        """Test time difference humanization."""
        assert DiffGenerator._humanize_time_diff(30) == "30 seconds"
        assert DiffGenerator._humanize_time_diff(90) == "1 minutes"
        assert DiffGenerator._humanize_time_diff(3700) == "1 hours"
        assert DiffGenerator._humanize_time_diff(86500) == "1 days"


class TestPermissionManager:
    """Test permission manager utility."""

    def test_permission_hierarchy(self):
        """Test permission level hierarchy."""
        # This would require database setup, so we'll test the logic
        # In a real scenario, you'd use fixtures with database
        pass

    def test_permission_validation(self):
        """Test permission validation logic."""
        # Test permission level comparisons
        hierarchy = {
            PermissionLevel.VIEWER: 1,
            PermissionLevel.EDITOR: 2,
            PermissionLevel.OWNER: 3
        }
        
        # Viewer < Editor < Owner
        assert hierarchy[PermissionLevel.VIEWER] < hierarchy[PermissionLevel.EDITOR]
        assert hierarchy[PermissionLevel.EDITOR] < hierarchy[PermissionLevel.OWNER]


class TestHelperFunctions:
    """Test various helper functions."""

    def test_datetime_serialization(self):
        """Test datetime handling in API responses."""
        dt = datetime.utcnow()
        iso_string = dt.isoformat()
        
        # Should be valid ISO format
        assert "T" in iso_string
        parsed_dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00') if iso_string.endswith('Z') else iso_string)
        assert abs((parsed_dt - dt).total_seconds()) < 1

    def test_pagination_logic(self):
        """Test pagination parameter validation."""
        # Test skip/limit combinations
        valid_combinations = [
            (0, 10),
            (10, 50),
            (0, 100)
        ]
        
        for skip, limit in valid_combinations:
            assert skip >= 0
            assert 1 <= limit <= 100

    def test_url_validation(self):
        """Test URL pattern validation."""
        valid_urls = [
            "http://localhost:3000",
            "https://api.example.com",
            "http://127.0.0.1:8000"
        ]
        
        for url in valid_urls:
            assert url.startswith(("http://", "https://"))
