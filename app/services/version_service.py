from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.event import Event, EventVersion
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
        
        # Create version record before rollback
        current_version = EventVersion(
            event_id=event.id,
            version_number=event.version,
            title=event.title,
            description=event.description,
            location=event.location,
            start_time=event.start_time,
            end_time=event.end_time,
            is_recurring=event.is_recurring,
            recurrence_type=event.recurrence_type,
            recurrence_pattern=event.recurrence_pattern,
            changed_by=user.id,
            change_summary=f"Rollback to version {version_number}"
        )
        db.add(current_version)
        
        # Apply rollback
        event.title = target_version.title
        event.description = target_version.description
        event.location = target_version.location
        event.start_time = target_version.start_time
        event.end_time = target_version.end_time
        event.is_recurring = target_version.is_recurring
        event.recurrence_type = target_version.recurrence_type
        event.recurrence_pattern = target_version.recurrence_pattern
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
        
        # Compare fields
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
            val1 = getattr(v1, field)
            val2 = getattr(v2, field)
            
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
            changelog_entry = {
                "version": version.version_number,
                "changed_by": version.changed_by,
                "changed_by_username": version.changed_by_user.username if version.changed_by_user else "Unknown",
                "change_summary": version.change_summary,
                "timestamp": version.created_at.isoformat(),
                "event_state": {
                    "title": version.title,
                    "description": version.description,
                    "location": version.location,
                    "start_time": version.start_time.isoformat(),
                    "end_time": version.end_time.isoformat(),
                    "is_recurring": version.is_recurring,
                    "recurrence_type": version.recurrence_type.value if version.recurrence_type else None
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
