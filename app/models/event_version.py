"""
Event version model for tracking event changes and history.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class EventVersion(Base):
    """
    Event version model for storing historical versions of events.
    
    This model tracks all changes made to events, allowing for
    version history, rollback, and diff functionality.
    """
    
    __tablename__ = "event_versions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to the main event
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Version information
    version_number = Column(Integer, nullable=False)
    
    # Event data snapshot (JSON representation of the event at this version)
    event_data = Column(JSON, nullable=False)
    
    # Change tracking
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_reason = Column(String(500), nullable=True)
    change_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Metadata
    is_current = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="versions")
    changed_by_user = relationship("User", foreign_keys=[changed_by])
    
    def __repr__(self):
        return f"<EventVersion(id={self.id}, event_id={self.event_id}, version={self.version_number})>"
    
    @property
    def change_timestamp(self):
        """Get the timestamp when this version was created."""
        return self.created_at
    
    def to_dict(self):
        """Convert version to dictionary representation."""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "version_number": self.version_number,
            "event_data": self.event_data,
            "changed_by": self.changed_by,
            "change_reason": self.change_reason,
            "change_summary": self.change_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_current": self.is_current
        }
