#!/usr/bin/env python3
"""
Development commands for the Event Management API.

This script provides useful commands for development and testing.
"""

import click
import uvicorn
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@click.group()
def cli():
    """Event Management API Development Commands"""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload/--no-reload', default=True, help='Enable auto-reload')
def runserver(host, port, reload):
    """Start the development server."""
    click.echo(f"🚀 Starting server at http://{host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

@cli.command()
def migrate():
    """Run database migrations."""
    click.echo("📊 Running database migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        click.echo("✅ Migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Migration failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--message', '-m', required=True, help='Migration message')
def makemigration(message):
    """Create a new migration."""
    click.echo(f"📝 Creating migration: {message}")
    try:
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
        click.echo("✅ Migration created successfully!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Migration creation failed: {e}")
        sys.exit(1)

@cli.command()
def setup():
    """Set up development environment."""
    click.echo("🛠️  Setting up development environment...")
    try:
        from scripts.setup_dev import main as setup_main
        setup_main()
    except ImportError:
        click.echo("❌ Could not import setup script")
        sys.exit(1)

@cli.command()
def test():
    """Run tests."""
    click.echo("🧪 Running tests...")
    try:
        subprocess.run(["pytest", "-v", "--tb=short"], check=True)
        click.echo("✅ All tests passed!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Tests failed: {e}")
        sys.exit(1)

@cli.command()
def lint():
    """Run code linting."""
    click.echo("🔍 Running code linting...")
    try:
        subprocess.run(["black", ".", "--check"], check=True)
        subprocess.run(["isort", ".", "--check-only"], check=True)
        subprocess.run(["flake8", "."], check=True)
        click.echo("✅ Code style is clean!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Linting failed: {e}")
        sys.exit(1)

@cli.command()
def format():
    """Format code."""
    click.echo("✨ Formatting code...")
    try:
        subprocess.run(["black", "."], check=True)
        subprocess.run(["isort", "."], check=True)
        click.echo("✅ Code formatted successfully!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Formatting failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()
