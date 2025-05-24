#!/usr/bin/env python3
"""
Script to create the initial database migration.

This script ensures all models are properly imported and creates
the initial migration for the database schema.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_alembic():
    """Check if Alembic is available."""
    try:
        result = subprocess.run(["alembic", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Alembic found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Alembic not working properly")
            return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install requirements first:")
        print("   pip install -r requirements.txt")
        return False

def create_migration():
    """Create the initial migration."""
    try:
        # Ensure we're in the project directory
        os.chdir(project_root)
        print(f"Working directory: {os.getcwd()}")
        
        # First, try to initialize alembic if not already done
        if not os.path.exists("alembic.ini"):
            print("❌ alembic.ini not found. Please ensure Alembic is properly configured.")
            return False
        
        # Create initial migration
        print("🔄 Creating initial database migration...")
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", 
            "-m", "Initial migration with users, events, and permissions"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Initial migration created successfully!")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Migration creation failed:")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def apply_migration():
    """Apply the migration to create tables."""
    try:
        print("📊 Applying database migrations...")
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrations applied successfully!")
            return True
        else:
            print(f"❌ Migration application failed:")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error applying migrations: {e}")
        return False

def main():
    """Create and apply initial migration."""
    print("🔄 Setting up database migrations...")
    
    # Check if Alembic is available
    if not check_alembic():
        sys.exit(1)
    
    # Create migration
    if not create_migration():
        sys.exit(1)
    
    # Apply migration
    if not apply_migration():
        sys.exit(1)
    
    print("✅ Database migration setup complete!")

if __name__ == "__main__":
    main()
