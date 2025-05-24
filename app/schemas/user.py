from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")

class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

class UserUpdate(BaseModel):
    """Schema for user updates."""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None

class UserInDB(UserBase):
    """Schema representing user as stored in database."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """Schema for user responses (excludes sensitive data)."""
    pass
