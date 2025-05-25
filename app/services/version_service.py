from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.event import Event
from app.models.event_version import EventVersion
from app.models.user import User
from app.models.permission import PermissionLevel
from app.utils.permissions import PermissionManager

class VersionService:
    """Service layer for event versioning operations."""
    
    @staticmethod
    def get_event_history(db: Session, event: Event, user: User) -> List[EventVersion]:
        """
        Get complete version history for an event.
        User must have at least viewer permission.
        """
        if not PermissionManager.has_permission(db, user, event, PermissionLevel.VIEWER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view event history"
            )
        
        return db.query(EventVersion).filter(
            EventVersion.event_id == event.id
        ).order_by(EventVersion.version_number.desc()).all()
    
    @staticmethod
    def get_version(db: Session, event: Event, version_number: int, user: User) -> Optional[EventVersion]:
        """
        Get specific version of an event.
        """
        if not PermissionManager.has_permission(db, user, event, PermissionLevel.VIEWER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view event version"
            )
        
        return db.query(EventVersion).filter(
            EventVersion.event_id == event.id,
            EventVersion.version_number == version_number
        ).first()
    
    @staticmethod
    def rollback_event(db: Session, event: Event, version_number: int, user: User) -> Event:
        """
        Rollback event to a previous version.
        Only owners and editors can perform rollbacks.
        """
        if not PermissionManager.has_permission(db, user, event, PermissionLevel.EDITOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to rollback event"
            )
        
        # Get target version
        target_version = db.query(EventVersion).filter(
            EventVersion.event_id == event.id,
            EventVersion.version_number == version_number
        ).first()
        
        if not target_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_number} not found"
            )
        
        # Import EventService to create version
        from app.services.event_service import EventService
        
        # Create version record before rollback
        EventService._create_version(db, event, user, f"Rollback to version {version_number}")
        
        # Apply rollback using event_data
        event_data = target_version.event_data
        from app.models.event import RecurrenceType
        
        event.title = event_data.get("title")
        event.description = event_data.get("description")
        event.location = event_data.get("location")
        event.start_time = datetime.fromisoformat(event_data.get("start_time")) if event_data.get("start_time") else None
        event.end_time = datetime.fromisoformat(event_data.get("end_time")) if event_data.get("end_time") else None
        event.is_recurring = event_data.get("is_recurring", False)
        event.recurrence_type = RecurrenceType(event_data.get("recurrence_type", "none"))
        event.recurrence_pattern = event_data.get("recurrence_pattern")
        event.version += 1
        event.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(event)
        
        return event
    
    @staticmethod
    def compare_versions(
        db: Session, 
        event: Event, 
        version1: int, 
        version2: int, 
        user: User
    ) -> Dict[str, Any]:
        """
        Compare two versions of an event and return differences.
        This is the highlighted diff functionality.
        """
        if not PermissionManager.has_permission(db, user, event, PermissionLevel.VIEWER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to compare versions"
            )
        
        # Get both versions
        v1 = db.query(EventVersion).filter(
            EventVersion.event_id == event.id,
            EventVersion.version_number == version1
        ).first()
        
        v2 = db.query(EventVersion).filter(
            EventVersion.event_id == event.id,
            EventVersion.version_number == version2
        ).first()
        
        if not v1 or not v2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both versions not found"
            )
        
        # Compare fields using event_data
        diff = {
            "version1": version1,
            "version2": version2,
            "changes": {},
            "summary": {
                "changed_fields": 0,
                "comparison_date": datetime.utcnow().isoformat()
            }
        }
        
        # Fields to compare
        comparable_fields = [
            "title", "description", "location", "start_time", "end_time",
            "is_recurring", "recurrence_type", "recurrence_pattern"
        ]
        
        for field in comparable_fields:
            val1 = v1.event_data.get(field)
            val2 = v2.event_data.get(field)
            
            if val1 != val2:
                diff["changes"][field] = {
                    f"version_{version1}": str(val1) if val1 is not None else None,
                    f"version_{version2}": str(val2) if val2 is not None else None,
                    "change_type": VersionService._determine_change_type(val1, val2)
                }
                diff["summary"]["changed_fields"] += 1
        
        return diff
    
    @staticmethod
    def get_changelog(db: Session, event: Event, user: User, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chronological changelog for an event.
        """
        if not PermissionManager.has_permission(db, user, event, PermissionLevel.VIEWER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view changelog"
            )
        
        versions = db.query(EventVersion).filter(
            EventVersion.event_id == event.id
        ).order_by(EventVersion.created_at.desc()).limit(limit).all()
        
        changelog = []
        for version in versions:
            event_data = version.event_data
            changelog_entry = {
                "version": version.version_number,
                "changed_by": version.changed_by,
                "changed_by_username": version.changed_by_user.username if version.changed_by_user else "Unknown",
                "change_summary": version.change_summary,
                "timestamp": version.created_at.isoformat(),
                "event_state": {
                    "title": event_data.get("title"),
                    "description": event_data.get("description"),
                    "location": event_data.get("location"),
                    "start_time": event_data.get("start_time"),
                    "end_time": event_data.get("end_time"),
                    "is_recurring": event_data.get("is_recurring"),
                    "recurrence_type": event_data.get("recurrence_type")
                }
            }
            changelog.append(changelog_entry)
        
        return changelog
    
    @staticmethod
    def _determine_change_type(old_value: Any, new_value: Any) -> str:
        """Determine the type of change between two values."""
        if old_value is None and new_value is not None:
            return "added"
        elif old_value is not None and new_value is None:
            return "removed"
        else:
            return "modified"
