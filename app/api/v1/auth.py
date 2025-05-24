from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TokenResponse, TokenRefresh
from app.schemas.user import UserCreate, UserResponse
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Rate limit registration attempts
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Creates user with hashed password and returns authentication tokens.
    Rate limited to prevent abuse.
    """
    try:
        # Create user
        user = AuthService.create_user(db, user_data)
        
        # Generate tokens
        tokens = AuthService.create_tokens(user)
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")  # Rate limit login attempts
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access tokens.
    
    Accepts either username or email with password.
    Rate limited to prevent brute force attacks.
    """
    user = AuthService.authenticate_user(db, login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = AuthService.create_tokens(user)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using valid refresh token.
    
    Allows clients to get new access tokens without re-authentication.
    """
    try:
        tokens = AuthService.refresh_access_token(db, token_data.refresh_token)
        return tokens
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user (placeholder for token blacklisting).
    
    In a production system, this would blacklist the current tokens.
    For now, it's a placeholder that confirms successful logout.
    """
    return {
        "message": "Successfully logged out",
        "user_id": current_user.id
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Returns user profile data excluding sensitive information.
    """
    return current_user
