from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.event import Event
from app.models.permission import EventPermission, PermissionLevel

class PermissionManager:
    """Utility class for managing event permissions."""
    
    @staticmethod
    def has_permission(
        db: Session, 
        user: User, 
        event: Event, 
        required_level: PermissionLevel
    ) -> bool:
        """
        Check if user has required permission level for event.
        Owner always has all permissions.
        """
        # Owner has all permissions
        if event.owner_id == user.id:
            return True
        
        # Check explicit permissions
        permission = db.query(EventPermission).filter(
            EventPermission.event_id == event.id,
            EventPermission.user_id == user.id
        ).first()
        
        if not permission:
            return False
        
        # Check if user's permission level meets or exceeds required level
        return permission.permission_level >= required_level
    
    @staticmethod
    def grant_permission(
        db: Session,
        event: Event,
        user_id: int,
        permission_level: PermissionLevel,
        granted_by: User
    ) -> EventPermission:
        """
        Grant permission to user for event.
        Validates that granter has authority to grant this permission level.
        """
        # Check if granter can grant this permission
        if event.owner_id != granted_by.id:
            granter_permission = db.query(EventPermission).filter(
                EventPermission.event_id == event.id,
                EventPermission.user_id == granted_by.id
            ).first()
            
            if not granter_permission or granter_permission.permission_level != PermissionLevel.OWNER:
                # Only owners and other owners can grant owner permissions
                if permission_level == PermissionLevel.OWNER:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Only owners can grant owner permissions"
                    )
                # Editors can only grant viewer permissions
                if (granter_permission and 
                    granter_permission.permission_level == PermissionLevel.EDITOR and
                    permission_level != PermissionLevel.VIEWER):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Editors can only grant viewer permissions"
                    )
        
        # Check if permission already exists
        existing_permission = db.query(EventPermission).filter(
            EventPermission.event_id == event.id,
            EventPermission.user_id == user_id
        ).first()
        
        if existing_permission:
            # Update existing permission
            existing_permission.permission_level = permission_level
            existing_permission.granted_by = granted_by.id
            db.commit()
            return existing_permission
        
        # Create new permission
        permission = EventPermission(
            event_id=event.id,
            user_id=user_id,
            permission_level=permission_level,
            granted_by=granted_by.id
        )
        
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    
    @staticmethod
    def revoke_permission(
        db: Session,
        event: Event,
        user_id: int,
        revoked_by: User
    ) -> bool:
        """
        Revoke user's permission for event.
        Only owners can revoke permissions.
        """
        if event.owner_id != revoked_by.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can revoke permissions"
            )
        
        permission = db.query(EventPermission).filter(
            EventPermission.event_id == event.id,
            EventPermission.user_id == user_id
        ).first()
        
        if permission:
            db.delete(permission)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_event_permissions(db: Session, event: Event) -> List[EventPermission]:
        """Get all permissions for an event."""
        return db.query(EventPermission).filter(
            EventPermission.event_id == event.id
        ).all()
    
    @staticmethod
    def get_user_events_with_permission(
        db: Session, 
        user: User, 
        permission_level: Optional[PermissionLevel] = None
    ) -> List[Event]:
        """
        Get all events user has access to, optionally filtered by permission level.
        """
        # Get owned events
        owned_events = db.query(Event).filter(
            Event.owner_id == user.id,
            Event.is_deleted == False
        )
        
        # Get events with explicit permissions
        permission_query = db.query(Event).join(EventPermission).filter(
            EventPermission.user_id == user.id,
            Event.is_deleted == False
        )
        
        if permission_level:
            permission_query = permission_query.filter(
                EventPermission.permission_level == permission_level
            )
        
        shared_events = permission_query.all()
        
        # Combine and deduplicate
        all_events = list(owned_events) + shared_events
        return list({event.id: event for event in all_events}.values())
