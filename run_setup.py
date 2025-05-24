#!/usr/bin/env python3
"""
Simple setup runner for the Event Management API.

This script provides an easy way to set up the development environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_setup():
    """Run the development setup."""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 Event Management API Setup")
    print("=" * 40)
    
    # Run the setup script
    try:
        print("Running setup script...")
        result = subprocess.run([
            sys.executable, "scripts/setup_dev.py"
        ], check=True)
        print("✅ Setup completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_setup()
