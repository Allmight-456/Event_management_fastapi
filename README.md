# 🗓️ Collaborative Event Management API

A robust FastAPI-based event management system with real-time collaboration, permission-based sharing, and comprehensive version tracking.

## ✨ Featuresumentation Screenshots

### Core Functionalityce
- **User Authentication & Authorization** - JWT-based with role-based access control
- **Event Management** - Full CRUD operations with conflict detection
- **Collaborative Sharing** - Hierarchical permission system (Owner/Editor/Viewer)
- **Version Control** - Complete audit trail with diff comparison
- **Rate Limiting** - Protection against abuse with configurable limits
- **Batch Operations** - Efficient bulk event creationnts*

### Advanced Features
- **Permission Hierarchy** - Granular access control for events
- **Event Versioning** - Track all changes with rollback capability
- **Diff Engine** - Compare versions with detailed change tracking
- **Conflict Detection** - Prevent scheduling conflicts
- **Audit Logging** - Complete changelog for complianceng)
*Permission-based sharing and collaboration endpoints*
## 🚀 Quick Start
### Version Control System
### Prerequisites API](./public/version-endpoints.png)
- Python 3.8+ning, diff comparison, and rollback functionality*
- PostgreSQL 12+
- Redis (optional, for caching)

### Installationnality
- **User Authentication & Authorization** - JWT-based with role-based access control
1. **Clone the repository**ll CRUD operations with conflict detection
```bashlaborative Sharing** - Hierarchical permission system (Owner/Editor/Viewer)
git clone <repository-url>mplete audit trail with diff comparison
cd neofi_python_fastapirotection against abuse with configurable limits
```*Batch Operations** - Efficient bulk event creation

2. **Create virtual environment**
```bashmission Hierarchy** - Granular access control for events
python -m venv venvg** - Track all changes with rollback capability
source venv/bin/activate  # On Windows: venv\Scripts\activatecking
```*Conflict Detection** - Prevent scheduling conflicts
- **Audit Logging** - Complete changelog for compliance
3. **Install dependencies**
```bashuick Start
pip install -r requirements.txt
``` Prerequisites
- Python 3.8+
4. **Set up PostgreSQL**
```bash (optional, for caching)
# Install PostgreSQL (macOS)
brew install postgresql@14
brew services start postgresql@14
1. **Clone the repository**
# Create database and user
createdb neofi_dbtory-url>
psql postgres -c "CREATE USER neofi_user WITH PASSWORD 'neofi_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE neofi_db TO neofi_user;"
psql postgres -c "ALTER USER neofi_user CREATEDB;"
```**Create virtual environment**
```bash
5. **Configure environment**
```bashvenv/bin/activate  # On Windows: venv\Scripts\activate
cp .env.example .env
# Edit .env with your database credentials
```**Install dependencies**
```bash
6. **Initialize database**s.txt
```bash
python -c "from app.core.database import init_db; init_db()"
```**Set up PostgreSQL**
```bash
7. **Start the server**acOS)
```bashstall postgresql@14
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
# Create database and user
## 📋 Environment Configuration
psql postgres -c "CREATE USER neofi_user WITH PASSWORD 'neofi_password';"
### Required Environment VariablesEGES ON DATABASE neofi_db TO neofi_user;"
psql postgres -c "ALTER USER neofi_user CREATEDB;"
```bash
# Database Configuration
DATABASE_URL=postgresql://neofi_user:neofi_password@localhost:5432/neofi_db
```bash
# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```bash
# API Configuration.core.database import init_db; init_db()"
API_V1_STR=/api/v1
PROJECT_NAME=Event Management API
VERSION=1.0.0e server**
```bash
# Environmentain:app --reload --host 0.0.0.0 --port 8000
ENVIRONMENT=development
DEBUG=true
```📋 Environment Configuration

### Optional Configurationariables

```bash
# Redis for caching and rate limiting
REDIS_URL=redis://localhost:6379user:neofi_password@localhost:5432/neofi_db

# CORS Originsfiguration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALGORITHM=HS256
# Rate LimitingPIRE_MINUTES=30
RATE_LIMIT_PER_MINUTE=100=7
```
# API Configuration
## 📸 API Documentation
PROJECT_NAME=Event Management API
### Swagger UI Interface
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==" alt="API Documentation" style="max-width: 100%;">

*Note: Replace the base64 string above with your actual screenshot*

Once the server is running, access the interactive API documentation:```

- **Swagger UI**: http://localhost:8000/docs### Optional Configuration
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📡 API Endpoints

### Authentication# CORS Origins
- `POST /api/v1/auth/register` - Register new userRS_ORIGINS=http://localhost:3000,http://localhost:8000
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - User logout

### Events
- `GET /api/v1/events/` - List events (with filtering)
- `POST /api/v1/events/` - Create event
- `GET /api/v1/events/{id}` - Get event detailsrunning, access the interactive API documentation:
- `PUT /api/v1/events/{id}` - Update event
- `DELETE /api/v1/events/{id}` - Delete event
- `POST /api/v1/events/batch` - Batch create events

### Version Control
- `GET /api/v1/events/{id}/history` - Get event history### Live API Testing
- `GET /api/v1/events/{id}/versions/{version}` - Get specific versionerface](./public/api-testing.png)
- `POST /api/v1/events/{id}/rollback/{version}` - Rollback to versionrface*
- `GET /api/v1/events/{id}/diff/{v1}/{v2}` - Compare versions
- `GET /api/v1/events/{id}/changelog` - Get changelog

### Collaboration
- `POST /api/v1/collaboration/{id}/share` - Share event
- `GET /api/v1/collaboration/{id}/permissions` - Get permissions
- `PUT /api/v1/collaboration/{id}/permissions/{user_id}` - Update permission
- `DELETE /api/v1/collaboration/{id}/permissions/{user_id}` - Revoke permission
- `GET /api/v1/collaboration/{id}/collaborators` - Get collaborators /api/v1/auth/register` - Register new user
in
## 🐳 Docker DeploymentGET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - User logout
### Build Docker Image
```bashnts
docker build -t event-management-api .s/` - List events (with filtering)
```POST /api/v1/events/` - Create event
- `GET /api/v1/events/{id}` - Get event details
### Run with Docker Composee event
```bashTE /api/v1/events/{id}` - Delete event
docker-compose up -dv1/events/batch` - Batch create events
```
### Version Control
### Environment-specific Deploymentv1/events/{id}/history` - Get event history
```bash
# DevelopmentPOST /api/v1/events/{id}/rollback/{version}` - Rollback to version
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d- `GET /api/v1/events/{id}/diff/{v1}/{v2}` - Compare versions
changelog` - Get changelog
# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```- `POST /api/v1/collaboration/{id}/share` - Share event
{id}/permissions` - Get permissions
## 🚀 Production Deployment/api/v1/collaboration/{id}/permissions/{user_id}` - Update permission
Revoke permission
### Using Docker (Recommended)GET /api/v1/collaboration/{id}/collaborators` - Get collaborators

1. **Build production image**
```bash
docker build -f Dockerfile.prod -t event-management-api:prod .
```
ker build -t event-management-api .
2. **Set up production environment**```
```bash
cp .env.production .env with Docker Compose
# Update with production values
```ker-compose up -d
```
3. **Deploy with Docker Compose**
```bash### Environment-specific Deployment
docker-compose -f docker-compose.prod.yml up -d
```opment
ose.yml -f docker-compose.dev.yml up -d
### Manual Deployment
roduction
1. **Set up production environment**docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```bash
export ENVIRONMENT=production
export DEBUG=false
```
### Using Docker (Recommended)
2. **Use production WSGI server**
```bash1. **Build production image**
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```build -f Dockerfile.prod -t event-management-api:prod .

## 🔧 Development
2. **Set up production environment**
### Running Tests
```bash.production .env
pytest production values
```

### Code Quality3. **Deploy with Docker Compose**
```bash
# Format codeose -f docker-compose.prod.yml up -d
black app/
isort app/
### Manual Deployment
# Lint code
flake8 app/t up production environment**
mypy app/
```
export DEBUG=false
### Database Migrations
```bash
# Generate migration2. **Use production WSGI server**
alembic revision --autogenerate -m "Description"
p -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
# Apply migrations
alembic upgrade head

# Rollback migration![Docker Deployment](./public/docker-deployment.png)
alembic downgrade -1eady Docker containers with health checks*
```

## 📊 Permission System.png)
*Health checks and performance monitoring*
### Hierarchy
- **Owner** - Full control (edit, delete, share, manage permissions)elopment
- **Editor** - Can edit events and create versions
- **Viewer** - Read-only access to events
``bash
### Sharing Events
```python
# Example: Share event with multiple users
POST /api/v1/collaboration/{event_id}/share Code Quality
{``bash
  "users": [ormat code
    {"user_id": 2, "permission_level": "editor"},black app/
    {"user_id": 3, "permission_level": "viewer"}
  ]
}
```

## 🔒 Security Features

- **JWT Authentication** with access/refresh tokens
- **Rate Limiting** to prevent abuse```bash
- **Permission-based Authorization** for all operations
- **Input Validation** with Pydantic schemasalembic revision --autogenerate -m "Description"
- **SQL Injection Protection** with SQLAlchemy ORM
- **CORS Configuration** for cross-origin requests

## 📈 Monitoring & Health Checks

- **Health Check**: `GET /health`alembic downgrade -1
- **Metrics**: `GET /metrics` (if monitoring enabled)
- **Database Status**: Included in health check

## 🔄 Version Control Features
### Hierarchy
### Event Versioningull control (edit, delete, share, manage permissions)
- Automatic version creation on updates and create versions
- Complete audit trail with user attributioness to events
- Rollback capability to any previous version
### Permission Flow Diagram
### Diff Enginem](./public/permission-hierarchy.png)
- Field-level change detection*Visual representation of the hierarchical permission system*
- Visual diff representation
- Changelog generation

## 🤝 Contributing
tion/{event_id}/share
1. Fork the repository{
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)    {"user_id": 2, "permission_level": "editor"},
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request  ]

## 📄 License```

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.![Event Sharing Interface](./public/event-sharing.png)
 with granular permission controls*
## 🙋‍♂️ Support

For support, email support@yourcompany.com or create an issue in the repository.
ess/refresh tokens
## 🗺️ Roadmap
horization** for all operations
- [ ] Email notifications for event changes Pydantic schemas
- [ ] Calendar integrations (Google Calendar, Outlook)h SQLAlchemy ORM





- [ ] Advanced analytics dashboard- [ ] Webhook notifications- [ ] Mobile app support- [ ] Advanced recurring event patterns- [ ] File attachments for events- **CORS Configuration** for cross-origin requests

### Security Implementation
![Security Features](./public/security-features.png)
*JWT token authentication and authorization flow*

## 🔄 Version Control Features

### Event Versioning
- Automatic version creation on updates
- Complete audit trail with user attribution
- Rollback capability to any previous version

### Diff Engine
- Field-level change detection
- Visual diff representation
- Changelog generation

![Version Control Demo](./app/public/img2.png)
*Event versioning and diff comparison functionality*

### Version History View
![Version History](./app/public/img1.png)
*Complete audit trail with detailed change tracking*

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

## 🎯 API Response Examples

### Event Creation Response
```json
{
  "id": 1,
  "title": "Team Meeting",
  "description": "Weekly team sync",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T11:00:00Z",
  "owner_id": 1,
  "version": 1,
  "created_at": "2024-01-10T08:00:00Z"
}
```

### Permission Sharing Response
```json
{
  "event_id": 1,
  "shared_with": [
    {
      "user_id": 2,
      "permission_level": "editor",
      "status": "granted"
    },
    {
      "user_id": 3,
      "permission_level": "viewer", 
      "status": "granted"
    }
  ],
  "message": "Event sharing completed"
}
```

### Version Diff Response
```json
{
  "event_id": 1,
  "comparison": {
    "version_1": 1,
    "version_2": 2,
    "changes": [
      {
        "field": "title",
        "old_value": "Team Meeting",
        "new_value": "All Hands Meeting",
        "change_type": "modified"
      }
    ]
  }
}
```

## 📱 Frontend Integration Ready

This API is designed to work seamlessly with modern frontend frameworks:

### React/Next.js Integration
![React Integration](./app/public/img2.png)
*Example React components consuming the API*

### Vue.js Integration  
![Vue Integration](./app/public/img1.png)
*Vue.js application with real-time event updates*

### Mobile App Support
![Mobile API](./app/public/img3.png)
*RESTful API perfect for mobile app development*
