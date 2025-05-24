# 🗓️ Collaborative Event Management API

A robust FastAPI-based event management system with real-time collaboration, permission-based sharing, and comprehensive version tracking.

## ✨ Features

### Core Functionality
- **User Authentication & Authorization** - JWT-based with role-based access control
- **Event Management** - Full CRUD operations with conflict detection
- **Collaborative Sharing** - Hierarchical permission system (Owner/Editor/Viewer)
- **Version Control** - Complete audit trail with diff comparison
- **Rate Limiting** - Protection against abuse with configurable limits
- **Batch Operations** - Efficient bulk event creation

### Advanced Features
- **Permission Hierarchy** - Granular access control for events
- **Event Versioning** - Track all changes with rollback capability
- **Diff Engine** - Compare versions with detailed change tracking
- **Conflict Detection** - Prevent scheduling conflicts
- **Audit Logging** - Complete changelog for compliance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd neofi_python_fastapi
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL**
```bash
# Install PostgreSQL (macOS)
brew install postgresql@14
brew services start postgresql@14

# Create database and user
createdb neofi_db
psql postgres -c "CREATE USER neofi_user WITH PASSWORD 'neofi_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE neofi_db TO neofi_user;"
psql postgres -c "ALTER USER neofi_user CREATEDB;"
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. **Initialize database**
```bash
python -c "from app.core.database import init_db; init_db()"
```

7. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Environment Configuration

### Required Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://neofi_user:neofi_password@localhost:5432/neofi_db

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Event Management API
VERSION=1.0.0

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Optional Configuration

```bash
# Redis for caching and rate limiting
REDIS_URL=redis://localhost:6379

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

## 🏗️ API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - User logout

### Events
- `GET /api/v1/events/` - List events (with filtering)
- `POST /api/v1/events/` - Create event
- `GET /api/v1/events/{id}` - Get event details
- `PUT /api/v1/events/{id}` - Update event
- `DELETE /api/v1/events/{id}` - Delete event
- `POST /api/v1/events/batch` - Batch create events

### Version Control
- `GET /api/v1/events/{id}/history` - Get event history
- `GET /api/v1/events/{id}/versions/{version}` - Get specific version
- `POST /api/v1/events/{id}/rollback/{version}` - Rollback to version
- `GET /api/v1/events/{id}/diff/{v1}/{v2}` - Compare versions
- `GET /api/v1/events/{id}/changelog` - Get changelog

### Collaboration
- `POST /api/v1/collaboration/{id}/share` - Share event
- `GET /api/v1/collaboration/{id}/permissions` - Get permissions
- `PUT /api/v1/collaboration/{id}/permissions/{user_id}` - Update permission
- `DELETE /api/v1/collaboration/{id}/permissions/{user_id}` - Revoke permission
- `GET /api/v1/collaboration/{id}/collaborators` - Get collaborators

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t event-management-api .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

### Environment-specific Deployment
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🚀 Production Deployment

### Using Docker (Recommended)

1. **Build production image**
```bash
docker build -f Dockerfile.prod -t event-management-api:prod .
```

2. **Set up production environment**
```bash
cp .env.production .env
# Update with production values
```

3. **Deploy with Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. **Set up production environment**
```bash
export ENVIRONMENT=production
export DEBUG=false
```

2. **Use production WSGI server**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔧 Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📊 Permission System

### Hierarchy
- **Owner** - Full control (edit, delete, share, manage permissions)
- **Editor** - Can edit events and create versions
- **Viewer** - Read-only access to events

### Sharing Events
```python
# Example: Share event with multiple users
POST /api/v1/collaboration/{event_id}/share
{
  "users": [
    {"user_id": 2, "permission_level": "editor"},
    {"user_id": 3, "permission_level": "viewer"}
  ]
}
```

## 🔒 Security Features

- **JWT Authentication** with access/refresh tokens
- **Rate Limiting** to prevent abuse
- **Permission-based Authorization** for all operations
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** with SQLAlchemy ORM
- **CORS Configuration** for cross-origin requests

## 📈 Monitoring & Health Checks

- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics` (if monitoring enabled)
- **Database Status**: Included in health check

## 🔄 Version Control Features

### Event Versioning
- Automatic version creation on updates
- Complete audit trail with user attribution
- Rollback capability to any previous version

### Diff Engine
- Field-level change detection
- Visual diff representation
- Changelog generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For support, email support@yourcompany.com or create an issue in the repository.

## 🗺️ Roadmap

- [ ] Email notifications for event changes
- [ ] Calendar integrations (Google Calendar, Outlook)
- [ ] File attachments for events
- [ ] Advanced recurring event patterns
- [ ] Mobile app support
- [ ] Webhook notifications
- [ ] Advanced analytics dashboard