from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from enum import Enum

class RecurrenceType(str, Enum):
    """
    Define recurrence patterns for events.
    This supports the requirement for customizable recurrence patterns.
    """
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Event(Base):
    """
    Main event model with versioning support.
    
    Design philosophy:
    - Each event maintains current state plus version history
    - JSON field stores recurrence patterns for flexibility
    - Foreign key relationships maintain data integrity
    - Soft delete approach preserves audit trail
    """
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    
    # Time management - critical for conflict detection
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Recurrence support
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_type = Column(SQLEnum(RecurrenceType), default=RecurrenceType.NONE)
    recurrence_pattern = Column(JSON, nullable=True)  # Flexible pattern storage
    
    # Ownership and access control
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Versioning system - crucial for collaboration features
    version = Column(Integer, default=1, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)  # Soft delete
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="owned_events")
    permissions = relationship("EventPermission", back_populates="event", cascade="all, delete-orphan")
    versions = relationship("EventVersion", back_populates="event", cascade="all, delete-orphan")
    
class EventVersion(Base):
    """
    Version history for events - enables rollback and diff functionality.
    
    This model captures complete event state at each version, allowing us to:
    - Track who made changes and when
    - Enable rollback to previous versions
    - Generate diffs between versions
    - Maintain complete audit trail
    """
    __tablename__ = "event_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # Snapshot of event data at this version
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_recurring = Column(Boolean, nullable=False)
    recurrence_type = Column(SQLEnum(RecurrenceType))
    recurrence_pattern = Column(JSON, nullable=True)
    
    # Change tracking
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_summary = Column(String(500), nullable=True)  # Brief description of changes
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="versions")
    changed_by_user = relationship("User")
