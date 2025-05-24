"""
Tests for authentication endpoints.

This module tests user registration, login, token refresh, and authentication flows.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_user_success(self, client: TestClient, db_session: Session):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "newuser"
        
        # Verify user was created in database
        user = db_session.query(User).filter(User.username == "newuser").first()
        assert user is not None
        assert user.email == "newuser@example.com"

    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with duplicate username."""
        user_data = {
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password123",
            "full_name": "Different User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,
            "password": "password123",
            "full_name": "Different User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_invalid_data(self, client: TestClient):
        """Test registration with invalid data."""
        # Test short password
        user_data = {
            "username": "user",
            "email": "user@example.com",
            "password": "short",
            "full_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_login_with_username_success(self, client: TestClient, test_user: User):
        """Test successful login with username."""
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["username"] == test_user.username

    def test_login_with_email_success(self, client: TestClient, test_user: User):
        """Test successful login with email."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == test_user.username

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username/email or password" in response.json()["detail"]

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password."""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401

    def test_refresh_token_success(self, client: TestClient, test_user: User):
        """Test successful token refresh."""
        # First login to get tokens
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Use refresh token
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        refresh_data = {
            "refresh_token": "invalid.token.here"
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        """Test getting current user information."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "id" in data
        assert "hashed_password" not in data  # Sensitive data should not be exposed

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    def test_logout(self, client: TestClient, auth_headers: dict):
        """Test user logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Successfully logged out" in data["message"]

    def test_logout_unauthorized(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthRateLimit:
    """Test rate limiting on auth endpoints."""

    def test_register_rate_limit(self, client: TestClient):
        """Test rate limiting on registration endpoint."""
        user_data_template = {
            "username": "user{}",
            "email": "user{}@example.com",
            "password": "password123",
            "full_name": "User {}"
        }
        
        # Make multiple registration attempts
        for i in range(7):  # Exceed the 5/minute limit
            user_data = {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "password123",
                "full_name": f"User {i}"
            }
            response = client.post("/api/v1/auth/register", json=user_data)
            
            if i < 5:
                assert response.status_code in [201, 400]  # Success or duplicate
            else:
                assert response.status_code == 429  # Rate limited

    def test_login_rate_limit(self, client: TestClient):
        """Test rate limiting on login endpoint."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        # Make multiple login attempts
        for i in range(12):  # Exceed the 10/minute limit
            response = client.post("/api/v1/auth/login", json=login_data)
            
            if i < 10:
                assert response.status_code == 401  # Unauthorized
            else:
                assert response.status_code == 429  # Rate limited
