from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.models.event import Event, EventVersion, RecurrenceType
from app.models.user import User
from app.models.permission import EventPermission, PermissionLevel
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.utils.permissions import PermissionManager

class EventService:
    """Service layer for event operations."""
    
    @staticmethod
    def create_event(db: Session, event_data: EventCreate, owner: User) -> Event:
        """
        Create a new event with conflict detection.
        Checks for overlapping events for the same user.
        """
        # Check for conflicts with existing events
        EventService._check_event_conflicts(db, owner.id, event_data.start_time, event_data.end_time)
        
        # Create event
        db_event = Event(
            title=event_data.title,
            description=event_data.description,
            location=event_data.location,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            is_recurring=event_data.is_recurring,
            recurrence_type=event_data.recurrence_type,
            recurrence_pattern=event_data.recurrence_pattern,
            owner_id=owner.id,
            version=1
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Create initial version
        EventService._create_version(db, db_event, owner, "Initial creation")
        
        return db_event
    
    @staticmethod
    def get_events(
        db: Session, 
        user: User,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        owned_only: bool = False
    ) -> List[Event]:
        """
        Get events accessible to user with filtering and pagination.
        """
        query = db.query(Event).filter(Event.is_deleted == False)
        
        if owned_only:
            query = query.filter(Event.owner_id == user.id)
        else:
            # Get events user owns or has permission to view
            accessible_events = or_(
                Event.owner_id == user.id,
                Event.id.in_(
                    db.query(EventPermission.event_id).filter(
                        EventPermission.user_id == user.id
                    )
                )
            )
            query = query.filter(accessible_events)
        
        # Date filtering
        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.end_time <= end_date)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        return db.query(Event).filter(
            Event.id == event_id,
            Event.is_deleted == False
        ).first()
    
    @staticmethod
    def update_event(
        db: Session, 
        event: Event, 
        event_data: EventUpdate, 
        user: User
    ) -> Event:
        """
        Update event with versioning support.
        Creates new version and checks for conflicts.
        """
        # Check permissions
        if not PermissionManager.has_permission(db, user, event, PermissionLevel.EDITOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update event"
            )
        
        # Prepare update data
        update_data = event_data.dict(exclude_unset=True)
        if not update_data:
            return event
        
        # Check for conflicts if time is being updated
        if 'start_time' in update_data or 'end_time' in update_data:
            new_start = update_data.get('start_time', event.start_time)
            new_end = update_data.get('end_time', event.end_time)
            EventService._check_event_conflicts(db, event.owner_id, new_start, new_end, exclude_event_id=event.id)
        
        # Create version before update
        change_summary = EventService._generate_change_summary(event, update_data)
        EventService._create_version(db, event, user, change_summary)
        
        # Update event
        for field, value in update_data.items():
            setattr(event, field, value)
        
        event.version += 1
        event.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(event)
        
        return event
    
    @staticmethod
    def delete_event(db: Session, event: Event, user: User) -> bool:
        """
        Soft delete event (only owner can delete).
        """
        if event.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only event owner can delete event"
            )
        
        # Create version before deletion
        EventService._create_version(db, event, user, "Event deleted")
        
        event.is_deleted = True
        event.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    
    @staticmethod
    def create_batch_events(db: Session, events_data: List[EventCreate], owner: User) -> List[Event]:
        """
        Create multiple events in a single transaction.
        All events must be valid or none are created.
        """
        created_events = []
        
        try:
            for event_data in events_data:
                # Check conflicts for each event
                EventService._check_event_conflicts(
                    db, owner.id, event_data.start_time, event_data.end_time
                )
                
                db_event = Event(
                    title=event_data.title,
                    description=event_data.description,
                    location=event_data.location,
                    start_time=event_data.start_time,
                    end_time=event_data.end_time,
                    is_recurring=event_data.is_recurring,
                    recurrence_type=event_data.recurrence_type,
                    recurrence_pattern=event_data.recurrence_pattern,
                    owner_id=owner.id,
                    version=1
                )
                
                db.add(db_event)
                created_events.append(db_event)
            
            db.commit()
            
            # Create initial versions for all events
            for event in created_events:
                db.refresh(event)
                EventService._create_version(db, event, owner, "Initial creation")
            
            return created_events
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Batch creation failed: {str(e)}"
            )
    
    @staticmethod
    def _check_event_conflicts(
        db: Session, 
        user_id: int, 
        start_time: datetime, 
        end_time: datetime,
        exclude_event_id: Optional[int] = None
    ):
        """
        Check for overlapping events for the same user.
        """
        query = db.query(Event).filter(
            Event.owner_id == user_id,
            Event.is_deleted == False,
            and_(
                Event.start_time < end_time,
                Event.end_time > start_time
            )
        )
        
        if exclude_event_id:
            query = query.filter(Event.id != exclude_event_id)
        
        conflicting_event = query.first()
        if conflicting_event:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event conflicts with existing event: {conflicting_event.title}"
            )
    
    @staticmethod
    def _create_version(db: Session, event: Event, user: User, change_summary: str):
        """Create a version record for the current event state."""
        version = EventVersion(
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
            change_summary=change_summary
        )
        
        db.add(version)
        db.commit()
    
    @staticmethod
    def _generate_change_summary(event: Event, update_data: Dict[str, Any]) -> str:
        """Generate a human-readable summary of changes."""
        changes = []
        
        for field, new_value in update_data.items():
            old_value = getattr(event, field)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
        
        return "Updated: " + ", ".join(changes) if changes else "No changes"
