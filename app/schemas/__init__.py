"""
Schemas package initialization.

This package contains Pydantic models for request/response validation
and serialization throughout the API.
"""

from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserInDB
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventBatchCreate
from app.schemas.auth import (
    LoginRequest, TokenResponse, TokenRefresh, TokenValidationResponse,
    LogoutRequest, PermissionShare, EventShareRequest, PermissionResponse,
    PermissionUpdateRequest
)

__all__ = [
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserInDB",
    "EventCreate",
    "EventUpdate",
    "EventResponse", 
    "EventBatchCreate",
    "LoginRequest",
    "TokenResponse",
    "TokenRefresh",
    "TokenValidationResponse",
    "LogoutRequest", 
    "PermissionShare",
    "EventShareRequest",
    "PermissionResponse",
    "PermissionUpdateRequest"
]
