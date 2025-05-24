from typing import Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token
)
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate

class AuthService:
    """Service layer for authentication operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password.
        Handles duplicate username/email validation.
        """
        # Check for existing username
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=UserRole.USER  # Default role
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed"
            )
    
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> Optional[User]:
        """
        Authenticate user with username/email and password.
        Returns user if authentication successful, None otherwise.
        """
        # Check if login is email or username
        if '@' in login_data.username:
            user = db.query(User).filter(User.email == login_data.username).first()
        else:
            user = db.query(User).filter(User.username == login_data.username).first()
        
        if not user or not user.is_active:
            return None
            
        if not verify_password(login_data.password, user.hashed_password):
            return None
            
        return user
    
    @staticmethod
    def create_tokens(user: User) -> TokenResponse:
        """
        Create access and refresh tokens for authenticated user.
        Returns complete token response with user information.
        """
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes in seconds
            user_id=user.id,
            username=user.username,
            role=user.role.value
        )
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
        """
        Generate new access token using valid refresh token.
        Validates refresh token and user status.
        """
        try:
            from app.core.security import verify_token
            payload = verify_token(refresh_token, token_type="refresh")
        except ImportError:
            # Fallback to manual JWT verification if verify_token doesn't exist
            from jose import jwt, JWTError
            from app.core.config import settings
            try:
                payload = jwt.decode(
                    refresh_token, 
                    settings.SECRET_KEY, 
                    algorithms=[settings.ALGORITHM]
                )
            except JWTError:
                payload = None
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return AuthService.create_tokens(user)
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
