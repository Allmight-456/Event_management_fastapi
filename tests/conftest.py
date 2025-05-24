"""
Pytest configuration and fixtures for the Event Management API tests.

This file contains shared fixtures and configuration that can be used
across all test modules.
"""

import pytest
import asyncio
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User, UserRole
from app.models.event import Event, RecurrenceType
from app.core.security import get_password_hash, create_access_token

# Test database URL - using SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test_event_management.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def test_db():
    """Create test database tables for the session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_db) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(test_db) -> TestClient:
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session: Session) -> User:
    """Create a test admin user."""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def test_user2(db_session: Session) -> User:
    """Create a second test user for collaboration tests."""
    user2 = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User Two",
        role=UserRole.USER
    )
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)
    return user2

@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """Create authentication headers for test user."""
    token_data = {
        "sub": test_user.id,
        "username": test_user.username,
        "role": test_user.role.value
    }
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(test_admin: User) -> Dict[str, str]:
    """Create authentication headers for admin user."""
    token_data = {
        "sub": test_admin.id,
        "username": test_admin.username,
        "role": test_admin.role.value
    }
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def sample_event_data() -> Dict[str, Any]:
    """Create sample event data for testing."""
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    return {
        "title": "Test Event",
        "description": "A test event for API testing",
        "location": "Test Location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "is_recurring": False,
        "recurrence_type": "none"
    }

@pytest.fixture
def test_event(db_session: Session, test_user: User) -> Event:
    """Create a test event."""
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    event = Event(
        title="Test Event",
        description="A test event",
        location="Test Location",
        start_time=start_time,
        end_time=end_time,
        is_recurring=False,
        recurrence_type=RecurrenceType.NONE,
        owner_id=test_user.id,
        version=1
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event

@pytest.fixture
def recurring_event_data() -> Dict[str, Any]:
    """Create sample recurring event data."""
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    return {
        "title": "Daily Standup",
        "description": "Daily team standup meeting",
        "location": "Conference Room A",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "is_recurring": True,
        "recurrence_type": "daily",
        "recurrence_pattern": {
            "interval": 1,
            "weekdays_only": True
        }
    }

# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
