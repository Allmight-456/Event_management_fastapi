from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.event import Event
from app.models.permission import EventPermission, PermissionLevel

# OAuth2 scheme for token extraction
security = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Extract and validate user from JWT token.
    This dependency ensures all protected endpoints have valid authentication.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_event_with_permission(
    event_id: int,
    required_permission: PermissionLevel,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Event:
    """
    Get event and verify user has required permission level.
    This dependency handles permission checking for event operations.
    """
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.is_deleted == False
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Owner always has all permissions
    if event.owner_id == current_user.id:
        return event
    
    # Check explicit permissions
    permission = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == current_user.id
    ).first()
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Verify permission level hierarchy
    permission_hierarchy = {
        PermissionLevel.VIEWER: 1,
        PermissionLevel.EDITOR: 2,
        PermissionLevel.OWNER: 3
    }
    
    if permission_hierarchy[permission.permission_level] < permission_hierarchy[required_permission]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return event

# Specific permission dependencies for common operations
def require_event_view_permission(event_id: int):
    """Dependency factory for view permission."""
    def _require_permission(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> Event:
        return get_event_with_permission(event_id, PermissionLevel.VIEWER, current_user, db)
    return _require_permission

def require_event_edit_permission(event_id: int):
    """Dependency factory for edit permission."""
    def _require_permission(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> Event:
        return get_event_with_permission(event_id, PermissionLevel.EDITOR, current_user, db)
    return _require_permission

def require_event_owner_permission(event_id: int):
    """Dependency factory for owner permission."""
    def _require_permission(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> Event:
        return get_event_with_permission(event_id, PermissionLevel.OWNER, current_user, db)
    return _require_permission
