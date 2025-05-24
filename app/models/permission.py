from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum

class PermissionLevel(str, Enum):
    """
    Define permission levels for event access control.
    Hierarchical permissions: VIEWER < EDITOR < OWNER
    """
    VIEWER = "viewer"    # Can view event details and history
    EDITOR = "editor"    # Can edit event details, create versions
    OWNER = "owner"      # Can do everything including delete and share
    
    def __lt__(self, other):
        """Enable comparison for hierarchical permissions"""
        if not isinstance(other, PermissionLevel):
            return NotImplemented
        order = {self.VIEWER: 1, self.EDITOR: 2, self.OWNER: 3}
        return order[self] < order[other]
    
    def __le__(self, other):
        """Less than or equal comparison"""
        return self < other or self == other
    
    def __gt__(self, other):
        """Greater than comparison"""
        if not isinstance(other, PermissionLevel):
            return NotImplemented
        return not self <= other
    
    def __ge__(self, other):
        """Greater than or equal comparison"""
        return self > other or self == other

class EventPermission(Base):
    """
    Event permission model for sharing events between users.
    
    This model implements fine-grained access control where:
    - Owners can grant any permission level
    - Editors can only grant viewer permissions
    - Viewers cannot grant permissions
    """
    __tablename__ = "event_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Permission details
    permission_level = Column(SQLEnum(PermissionLevel), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    event = relationship("Event", back_populates="permissions")
    user = relationship("User", back_populates="permissions", foreign_keys=[user_id])
    granted_by_user = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<EventPermission(event_id={self.event_id}, user_id={self.user_id}, level={self.permission_level})>"
