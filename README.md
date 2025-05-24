Base URL: http://localhost:8000

Authentication:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- GET  /api/v1/auth/me

Events:
- GET    /api/v1/events/
- POST   /api/v1/events/
- POST   /api/v1/events/batch
- GET    /api/v1/events/{event_id}
- PUT    /api/v1/events/{event_id}
- DELETE /api/v1/events/{event_id}

Event Versioning:
- GET  /api/v1/events/{event_id}/history
- GET  /api/v1/events/{event_id}/versions/{version_number}
- POST /api/v1/events/{event_id}/rollback/{version_number}
- GET  /api/v1/events/{event_id}/diff/{version1}/{version2}
- GET  /api/v1/events/{event_id}/changelog

Collaboration:
- POST   /api/v1/events/{event_id}/share
- GET    /api/v1/events/{event_id}/permissions
- PUT    /api/v1/events/{event_id}/permissions/{user_id}
- DELETE /api/v1/events/{event_id}/permissions/{user_id}
- GET    /api/v1/events/{event_id}/collaborators

Documentation:
- GET /docs (Swagger UI)
- GET /redoc (ReDoc)
- GET /openapi.json

Health Checks:
- GET /
- GET /health