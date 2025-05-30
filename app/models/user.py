from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
import enum
from datetime import datetime

class UserRole(str, Enum):
    """
    Define user roles for the system.
    This enum approach ensures type safety and prevents invalid role assignments.
    """
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """
    User model representing system users.
    
    Key design decisions:
    - Email is unique and used for login along with username
    - Timestamps track account creation and updates
    - Role-based access control is implemented through UserRole enum
    - Password is hashed before storage (handled in service layer)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Automatic timestamps for audit purposes
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    owned_events = relationship("Event", back_populates="owner")
    permissions = relationship("EventPermission", back_populates="user", foreign_keys="EventPermission.user_id")
    granted_permissions = relationship("EventPermission", foreign_keys="EventPermission.granted_by")
