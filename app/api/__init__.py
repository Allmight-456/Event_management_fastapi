"""
API package initialization.

This package contains all API-related modules including
endpoints, dependencies, and routing configuration.
"""

from app.api import deps
from app.api.v1 import auth, events, collaboration

__all__ = ["deps", "auth", "events", "collaboration"]
