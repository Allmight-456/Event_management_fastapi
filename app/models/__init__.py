"""
Models package initialization.

This file ensures all models are imported and available for Alembic migrations.
It's crucial that all models are imported here so that Alembic can detect them
for automatic migration generation.
"""

from app.models.user import User, UserRole
from app.models.event import Event, EventVersion, RecurrenceType
from app.models.permission import EventPermission, PermissionLevel

__all__ = [
    "User",
    "UserRole", 
    "Event",
    "EventVersion",
    "RecurrenceType",
    "EventPermission",
    "PermissionLevel"
]
