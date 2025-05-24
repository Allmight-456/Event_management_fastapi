#!/usr/bin/env python3
"""
Development setup script.

This script helps set up the development environment by:
1. Creating database tables
2. Running initial migrations
3. Creating sample data for testing
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for development
os.environ.setdefault('PYTHONPATH', str(project_root))

def setup_database():
    """Set up database and create tables."""
    try:
        # Import after setting up the path
        from app.core.database import engine, Base
        from app.core.config import settings
        
        print(f"Using database: {settings.DATABASE_URL}")
        
        # Import all models to ensure they're registered with Base
        import app.models.user
        import app.models.event  
        import app.models.permission
        
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        
        # Provide specific help for common issues
        if "psycopg2" in str(e):
            print("\n💡 PostgreSQL connection failed.")
            print("   The setup script is configured to use SQLite by default.")
            print("   Please check your .env file and DATABASE_URL setting.")
        elif "sqlite" in str(e).lower():
            print("\n💡 SQLite error occurred.")
            print("   This might be a file permission issue.")
        
        return False

def create_sample_data():
    """Create sample users and events for testing."""
    try:
        # Import after setting up the path
        from sqlalchemy.orm import Session
        from app.core.database import SessionLocal
        from app.models.user import User, UserRole
        from app.models.event import Event, RecurrenceType
        from app.core.security import get_password_hash
        from datetime import datetime, timedelta
        
        print("Creating sample data...")
        
        db = SessionLocal()
        try:
            # Check if data already exists
            if db.query(User).first():
                print("Sample data already exists, skipping...")
                return True
            
            # Create sample users
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN
            )
            
            test_user1 = User(
                username="testuser1",
                email="test1@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Test User One",
                role=UserRole.USER
            )
            
            test_user2 = User(
                username="testuser2",
                email="test2@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Test User Two",
                role=UserRole.USER
            )
            
            db.add_all([admin_user, test_user1, test_user2])
            db.commit()
            db.refresh(admin_user)
            db.refresh(test_user1)
            
            # Create sample events
            tomorrow = datetime.utcnow() + timedelta(days=1)
            next_week = datetime.utcnow() + timedelta(days=7)
            
            event1 = Event(
                title="Team Standup",
                description="Daily team standup meeting",
                location="Conference Room A",
                start_time=tomorrow.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=tomorrow.replace(hour=9, minute=30, second=0, microsecond=0),
                is_recurring=True,
                recurrence_type=RecurrenceType.DAILY,
                recurrence_pattern={"days": 1, "weekdays_only": True},
                owner_id=test_user1.id,
                version=1
            )
            
            event2 = Event(
                title="Project Planning",
                description="Sprint planning session",
                location="Virtual Meeting",
                start_time=next_week.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=next_week.replace(hour=16, minute=0, second=0, microsecond=0),
                is_recurring=False,
                recurrence_type=RecurrenceType.NONE,
                owner_id=test_user1.id,
                version=1
            )
            
            db.add_all([event1, event2])
            db.commit()
            
            print("✅ Sample data created successfully!")
            print(f"   - Admin user: admin@example.com / admin123")
            print(f"   - Test user 1: test1@example.com / password123")
            print(f"   - Test user 2: test2@example.com / password123")
            print(f"   - Created {db.query(Event).count()} sample events")
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_environment():
    """Check if the environment is properly set up."""
    try:
        # Check if we can import the main modules
        from app.core.config import settings
        from app.core.database import Base
        
        print("✅ Environment check passed!")
        print(f"   - Database URL: {settings.DATABASE_URL}")
        print(f"   - Debug mode: {settings.DEBUG}")
        return True
    except ImportError as e:
        print(f"❌ Environment check failed: {e}")
        print("Please ensure you're running this script from the project root directory")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up development environment...")
    print("=" * 50)
    
    # Change to project root directory
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Set up database
    if not setup_database():
        print("\n💡 Setup failed. Common solutions:")
        print("   1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check your .env file for correct DATABASE_URL")
        print("   3. For SQLite (default), ensure you have write permissions in the project directory")
        print("   4. For PostgreSQL, ensure the server is running and accessible")
        sys.exit(1)
    
    # Create sample data
    if not create_sample_data():
        sys.exit(1)
    
    print("=" * 50)
    print("✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Start the development server:")
    print("   uvicorn app.main:app --reload")
    print("   OR")
    print("   python -m uvicorn app.main:app --reload")
    print("\n2. Visit the API documentation:")
    print("   http://localhost:8000/docs")
    print("\n3. Test the API endpoints using the sample data")
    print("\n4. Use the sample credentials to test authentication:")
    print("   - Admin: admin@example.com / admin123")
    print("   - User: test1@example.com / password123")

if __name__ == "__main__":
    main()
