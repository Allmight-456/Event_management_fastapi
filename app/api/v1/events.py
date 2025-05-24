from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.services.event_service import EventService
from app.services.version_service import VersionService
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventBatchCreate
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.event import Event
from app.utils.diff import DiffGenerator

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_event(
    request: Request,  # Required for rate limiting
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new event with conflict detection.
    Automatically creates initial version for tracking.
    """
    event = EventService.create_event(db, event_data, current_user)
    return event

@router.post("/batch", response_model=List[EventResponse], status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_batch_events(
    request: Request,  # Required for rate limiting
    batch_data: EventBatchCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create multiple events in a single transaction.
    All events must be valid or none are created.
    """
    events = EventService.create_batch_events(db, batch_data.events, current_user)
    return events

@router.get("/", response_model=List[EventResponse])
@limiter.limit("30/minute")
async def get_events_list(
    request: Request,  # Required for rate limiting
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of events to return"),
    start_date: Optional[datetime] = Query(None, description="Filter events starting after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events ending before this date"),
    owned_only: bool = Query(False, description="Return only events owned by current user"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get events accessible to the current user with filtering options.
    Supports pagination and date range filtering.
    """
    events = EventService.get_events(
        db, current_user, skip, limit, start_date, end_date, owned_only
    )
    return events

@router.get("/{event_id}", response_model=EventResponse)
@limiter.limit("60/minute")
async def get_event(
    request: Request,  # Required for rate limiting
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific event by ID.
    User must have at least viewer permission.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check permission through service layer
    from app.utils.permissions import PermissionManager
    from app.models.permission import PermissionLevel
    
    if not PermissionManager.has_permission(db, current_user, event, PermissionLevel.VIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view event"
        )
    
    return event

@router.put("/{event_id}", response_model=EventResponse)
@limiter.limit("10/minute")
async def update_event(
    request: Request,  # Required for rate limiting
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an event with versioning support.
    Creates new version and checks for scheduling conflicts.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    updated_event = EventService.update_event(db, event, event_data, current_user)
    return updated_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_event(
    request: Request,  # Required for rate limiting
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete an event (only owner can delete).
    Creates final version record before deletion.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    EventService.delete_event(db, event, current_user)

# Version management endpoints
@router.get("/{event_id}/history")
@limiter.limit("30/minute")
async def get_event_history(
    request: Request,  # Required for rate limiting
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get complete version history for an event.
    Returns chronological list of all changes.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    history = VersionService.get_event_history(db, event, current_user)
    return {"event_id": event_id, "versions": history}

@router.get("/{event_id}/versions/{version_number}")
@limiter.limit("30/minute")
async def get_event_version(
    request: Request,  # Required for rate limiting
    event_id: int,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific version of an event.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    version = VersionService.get_version(db, event, version_number, current_user)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return version

@router.post("/{event_id}/rollback/{version_number}", response_model=EventResponse)
@limiter.limit("5/minute")
async def rollback_event(
    request: Request,  # Required for rate limiting
    event_id: int,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Rollback event to a previous version.
    Only editors and owners can perform rollbacks.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    rolled_back_event = VersionService.rollback_event(db, event, version_number, current_user)
    return rolled_back_event

@router.get("/{event_id}/diff/{version1}/{version2}")
@limiter.limit("20/minute")
async def compare_versions(
    request: Request,  # Required for rate limiting
    event_id: int,
    version1: int,
    version2: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compare two versions of an event - HIGHLIGHTED DIFF FUNCTIONALITY.
    Returns detailed field-by-field comparison showing what changed.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    diff = VersionService.compare_versions(db, event, version1, version2, current_user)
    return diff

@router.get("/{event_id}/changelog")
@limiter.limit("30/minute")
async def get_event_changelog(
    request: Request,  # Required for rate limiting
    event_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of changelog entries to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get chronological changelog for an event.
    Shows who made what changes and when.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    changelog = VersionService.get_changelog(db, event, current_user, limit)
    return {
        "event_id": event_id,
        "changelog": changelog
    }
