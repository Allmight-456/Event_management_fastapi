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
