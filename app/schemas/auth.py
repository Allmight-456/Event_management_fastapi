from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from app.models.permission import PermissionLevel

class LoginRequest(BaseModel):
    """
    Schema for login requests.
    
    This schema handles both username and email-based login attempts.
    The flexible approach allows users to authenticate with either credential.
    """
    username: str = Field(..., min_length=3, description="Username or email address")
    password: str = Field(..., min_length=1, description="User password")
    
    @validator('username')
    def validate_username_or_email(cls, v):
        """
        Accept either username (3+ chars) or valid email format.
        This provides flexibility for user authentication preferences.
        """
        if '@' in v:
            # If it contains @, treat as email and validate format will be handled by EmailStr if needed
            return v.lower().strip()
        elif len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v.lower().strip()

class TokenResponse(BaseModel):
    """
    Schema for authentication token responses.
    
    This comprehensive response provides all necessary information
    for the client to manage authentication state effectively.
    """
    access_token: str = Field(..., description="JWT access token for API authentication")
    refresh_token: str = Field(..., description="JWT refresh token for token renewal")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer' for JWT)")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    user_id: int = Field(..., description="Authenticated user's ID")
    username: str = Field(..., description="Authenticated user's username")
    role: str = Field(..., description="User's role in the system")

class TokenRefresh(BaseModel):
    """
    Schema for token refresh requests.
    
    When access tokens expire, clients can use their refresh token
    to obtain new access tokens without requiring re-authentication.
    """
    refresh_token: str = Field(..., min_length=10, description="Valid refresh token")

class TokenValidationResponse(BaseModel):
    """
    Schema for token validation responses.
    
    Used internally to validate and decode JWT tokens,
    providing user context for authenticated requests.
    """
    user_id: int = Field(..., description="User ID from token")
    username: str = Field(..., description="Username from token")
    role: str = Field(..., description="User role from token")
    exp: int = Field(..., description="Token expiration timestamp")
    is_valid: bool = Field(..., description="Whether token is currently valid")

class LogoutRequest(BaseModel):
    """
    Schema for logout requests.
    
    While JWT tokens are stateless, we may want to blacklist
    specific tokens for security purposes in the future.
    """
    refresh_token: Optional[str] = Field(None, description="Refresh token to invalidate")

class PermissionShare(BaseModel):
    """
    Schema for sharing events with specific permissions.
    
    This schema ensures that permission sharing requests
    contain valid user IDs and permission levels.
    """
    user_id: int = Field(..., gt=0, description="ID of user to share with")
    permission_level: PermissionLevel = Field(..., description="Permission level to grant")
    
    @validator('permission_level')
    def validate_permission_level(cls, v):
        """
        Ensure only valid permission levels are accepted.
        This prevents assignment of invalid or non-existent permissions.
        """
        if v not in [PermissionLevel.OWNER, PermissionLevel.EDITOR, PermissionLevel.VIEWER]:
            raise ValueError('Invalid permission level')
        return v

class EventShareRequest(BaseModel):
    """
    Schema for event sharing requests.
    
    Supports sharing events with multiple users simultaneously,
    each with their own specific permission level.
    """
    users: List[PermissionShare] = Field(
        ..., 
        min_items=1, 
        max_items=50,  # Reasonable limit to prevent abuse
        description="Users and their permissions (max 50 per request)"
    )
    
    @validator('users')
    def validate_unique_users(cls, v):
        """
        Ensure no duplicate user IDs in a single sharing request.
        This prevents confusion and potential permission conflicts.
        """
        user_ids = [user.user_id for user in v]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError('Cannot share with the same user multiple times in one request')
        return v

class PermissionResponse(BaseModel):
    """
    Schema for permission-related responses.
    
    Provides comprehensive information about a user's
    permissions on a specific event.
    """
    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    permission_level: PermissionLevel = Field(..., description="Permission level")
    granted_by: int = Field(..., description="ID of user who granted permission")
    granted_at: str = Field(..., description="ISO timestamp when permission was granted")
    updated_at: Optional[str] = Field(None, description="ISO timestamp of last permission update")

class PermissionUpdateRequest(BaseModel):
    """
    Schema for updating existing permissions.
    
    Allows modification of a user's permission level
    without requiring complete re-sharing of the event.
    """
    permission_level: PermissionLevel = Field(..., description="New permission level")
    
    @validator('permission_level')
    def validate_permission_level(cls, v):
        """Ensure only valid permission levels are accepted."""
        if v not in [PermissionLevel.OWNER, PermissionLevel.EDITOR, PermissionLevel.VIEWER]:
            raise ValueError('Invalid permission level')
        return v

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: int
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True