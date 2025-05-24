from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.event_service import EventService
from app.schemas.auth import EventShareRequest, PermissionResponse, PermissionUpdateRequest
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.permission import EventPermission, PermissionLevel
from app.utils.permissions import PermissionManager

router = APIRouter()

@router.post("/{event_id}/share", status_code=status.HTTP_201_CREATED)
async def share_event(
    event_id: int,
    share_request: EventShareRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Share an event with multiple users with specific permission levels.
    Only owners can share events with others.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Verify current user can share this event
    if not PermissionManager.has_permission(db, current_user, event, PermissionLevel.OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can share events"
        )
    
    # Validate all target users exist
    user_ids = [permission_share.user_id for permission_share in share_request.users]
    existing_users = db.query(User).filter(User.id.in_(user_ids)).all()
    existing_user_ids = {user.id for user in existing_users}
    
    missing_users = set(user_ids) - existing_user_ids
    if missing_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Users not found: {list(missing_users)}"
        )
    
    # Grant permissions
    granted_permissions = []
    for permission_share in share_request.users:
        try:
            permission = PermissionManager.grant_permission(
                db, event, permission_share.user_id, 
                permission_share.permission_level, current_user
            )
            granted_permissions.append({
                "user_id": permission_share.user_id,
                "permission_level": permission_share.permission_level.value,
                "status": "granted"
            })
        except HTTPException as e:
            granted_permissions.append({
                "user_id": permission_share.user_id,
                "permission_level": permission_share.permission_level.value,
                "status": "failed",
                "error": e.detail
            })
    
    return {
        "event_id": event_id,
        "shared_with": granted_permissions,
        "message": "Event sharing completed"
    }

@router.get("/{event_id}/permissions", response_model=List[PermissionResponse])
async def get_event_permissions(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all permissions for an event.
    Users can see permissions if they have any access to the event.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user has access to view permissions
    if not PermissionManager.has_permission(db, current_user, event, PermissionLevel.VIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view event permissions"
        )
    
    permissions = PermissionManager.get_event_permissions(db, event)
    
    # Convert to response format
    permission_responses = []
    for perm in permissions:
        permission_responses.append(PermissionResponse(
            user_id=perm.user_id,
            username=perm.user.username,
            permission_level=perm.permission_level,
            granted_by=perm.granted_by,
            granted_at=perm.granted_at.isoformat(),
            updated_at=perm.updated_at.isoformat() if perm.updated_at else None
        ))
    
    # Add owner information
    owner_permission = PermissionResponse(
        user_id=event.owner_id,
        username=event.owner.username,
        permission_level=PermissionLevel.OWNER,
        granted_by=event.owner_id,
        granted_at=event.created_at.isoformat(),
        updated_at=None
    )
    permission_responses.insert(0, owner_permission)
    
    return permission_responses

@router.put("/{event_id}/permissions/{user_id}")
async def update_user_permission(
    event_id: int,
    user_id: int,
    permission_update: PermissionUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's permission level for an event.
    Only owners can modify permissions.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Verify target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cannot modify owner's permissions
    if user_id == event.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify owner's permissions"
        )
    
    # Update permission
    permission = PermissionManager.grant_permission(
        db, event, user_id, permission_update.permission_level, current_user
    )
    
    return {
        "event_id": event_id,
        "user_id": user_id,
        "new_permission_level": permission_update.permission_level.value,
        "message": "Permission updated successfully"
    }

@router.delete("/{event_id}/permissions/{user_id}")
async def revoke_user_permission(
    event_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a user's permission for an event.
    Only owners can revoke permissions.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Cannot revoke owner's permissions
    if user_id == event.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke owner's permissions"
        )
    
    success = PermissionManager.revoke_permission(db, event, user_id, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return {
        "event_id": event_id,
        "user_id": user_id,
        "message": "Permission revoked successfully"
    }

@router.get("/{event_id}/collaborators")
async def get_event_collaborators(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all users who have access to an event (including owner).
    Useful for collaboration interfaces.
    """
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user has access to view collaborators
    if not PermissionManager.has_permission(db, current_user, event, PermissionLevel.VIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view collaborators"
        )
    
    collaborators = []
    
    # Add owner
    collaborators.append({
        "user_id": event.owner_id,
        "username": event.owner.username,
        "full_name": event.owner.full_name,
        "role": "owner",
        "permission_level": PermissionLevel.OWNER.value,
        "since": event.created_at.isoformat()
    })
    
    # Add users with explicit permissions
    permissions = PermissionManager.get_event_permissions(db, event)
    for perm in permissions:
        collaborators.append({
            "user_id": perm.user_id,
            "username": perm.user.username,
            "full_name": perm.user.full_name,
            "role": "collaborator",
            "permission_level": perm.permission_level.value,
            "since": perm.granted_at.isoformat()
        })
    
    return {
        "event_id": event_id,
        "total_collaborators": len(collaborators),
        "collaborators": collaborators
    }
