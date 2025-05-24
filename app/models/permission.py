from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PermissionLevel(str, enum.Enum):
    """
    Define permission levels for collaborative features.
    
    This hierarchy allows granular access control:
    - OWNER: Full control, can delete event and manage all permissions
    - EDITOR: Can modify event details and manage viewer permissions
    - VIEWER: Read-only access to event details
    """
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class EventPermission(Base):
    """
    Junction table for event sharing with role-based permissions.
    
    Design considerations:
    - Unique constraint prevents duplicate permissions for same user/event
    - Timestamps track when permissions were granted/modified
    - Supports the collaborative editing requirements
    """
    __tablename__ = "event_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_level = Column(Enum(PermissionLevel), nullable=False)
    
    # Audit trail for permission changes
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    event = relationship("Event", back_populates="permissions")
    user = relationship("User", back_populates="permissions")
    granted_by_user = relationship("User", foreign_keys=[granted_by])
    
    # Ensure one permission per user per event
    __table_args__ = (UniqueConstraint('event_id', 'user_id', name='unique_event_user_permission'),)
