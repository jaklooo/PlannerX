# PlannerX - Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-10-22

### Added - Initial Release (MVP)

#### Core Features
- User authentication via Firebase Auth with backend token verification
- Tasks management with CRUD operations
- Projects for organizing tasks
- Priority levels (LOW, MEDIUM, HIGH) for tasks
- Task statuses (TODO, DOING, DONE)
- Events/calendar with recurring rules (NONE, DAILY, WEEKLY, MONTHLY)
- Contacts management with birthday and name day tracking
- Daily email digest sent at 07:00 Europe/Prague
- RSS news integration with caching
- Optional SMS notifications via Twilio

#### Technical Implementation
- Flask application with blueprint architecture
- SQLAlchemy ORM with 5 models (User, Task, Event, Contact, Project)
- Alembic database migrations
- APScheduler for scheduled jobs
- Jinja2 templates with responsive CSS
- User data isolation and security
- CSRF protection
- Environment-based configuration
- SQLite for development, PostgreSQL support for production

#### Developer Experience
- Comprehensive README with setup instructions
- Quick start guide (QUICKSTART.md)
- Development seed script for demo data
- Unit tests with pytest (8+ tests)
- Code formatting with black and ruff
- Type hints for mypy
- Makefile for common tasks
- Docker support with Dockerfile and docker-compose
- Gunicorn production server configuration

#### Utilities
- Manual digest trigger script
- Test email sender
- CSV export/import for tasks
- Task snooze functionality (postpone by 1 day)

#### Documentation
- Detailed README.md
- Quick start guide
- Firebase Auth setup instructions
- SMTP configuration guide
- Production deployment guide
- API endpoint documentation
- Troubleshooting section

### Security
- Firebase token verification on backend
- User data strictly isolated by user_id
- SQL injection prevention via SQLAlchemy
- XSS prevention via Jinja2 autoescaping
- No hardcoded secrets
- Environment variables for sensitive data

### Known Issues
- Simplified Firebase token verification (consider PyJWT for production)
- No pagination for large lists
- Synchronous email sending (consider async for production)
- File-based RSS cache (consider Redis for production)

---

## Future Versions (Planned)

### [1.1.0] - TBD
- Pagination for tasks and events
- Advanced search functionality
- Tags/labels for tasks
- Task attachments support
- Dark mode toggle

### [1.2.0] - TBD
- Calendar view (month/year)
- Collaborative projects
- Activity history/log
- Real-time notifications

### [2.0.0] - TBD
- Mobile app (React Native)
- Desktop notifications
- Multi-language support
- Advanced analytics

---

**Format:** Based on [Keep a Changelog](https://keepachangelog.com/)  
**Versioning:** [Semantic Versioning](https://semver.org/)
