"""
Models package initialization.

This module imports all models to ensure they are registered with SQLAlchemy Base.
"""

# Import all models to register them with SQLAlchemy
from app.models.user import User, UserRole
from app.models.event import Event, RecurrenceType
from app.models.permission import EventPermission, PermissionLevel
from app.models.event_version import EventVersion

# Export all models for easy importing
__all__ = [
    "User",
    "UserRole", 
    "Event",
    "RecurrenceType",
    "EventPermission",
    "PermissionLevel",
    "EventVersion"
]
