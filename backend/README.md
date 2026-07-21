# SIRMS Backend API

Stock & Infrastructure Resource Management System - FastAPI backend for asset, incident, and maintenance management.

## Overview

SIRMS Backend is a comprehensive REST API for managing:
- **Assets**: Track equipment, devices, and infrastructure
- **Incidents**: Report and manage issues, assign work orders
- **Maintenance**: Schedule preventive/corrective maintenance, track execution
- **Stock**: Manage inventory levels, transactions, transfers
- **Infrastructure**: Organize locations, positions, and hierarchies

Built with **FastAPI**, **SQLAlchemy 2.x**, and **PostgreSQL**.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip or poetry

### Installation

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev,export]"
   ```

4. **Configure database** (create `.env` file in backend folder):
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/sirms_db
   TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

5. **Initialize database**:
   ```bash
   # Create PostgreSQL database
   createdb sirms_db
   
   # Run DDL scripts to create schema
   psql -U postgres -d sirms_db < database/deploy.sql
   ```

6. **Run development server**:
   ```bash
   python main.py
   # or
   uvicorn main:app --reload
   ```

   API available at http://localhost:8000
   Docs at http://localhost:8000/docs

## Architecture

### Layered Design

```
routes (api/v1/)
  ↓
services (business logic)
  ↓
repositories (data access)
  ↓
models (ORM)
  ↓
database (PostgreSQL)
```

### Key Components

- **Models** (`app/models/`): SQLAlchemy ORM for 6 database schemas (security, master, common, infrastructure, asset, incident)
- **Schemas** (`app/schemas/`): Pydantic v2 validation for all endpoint inputs/outputs
- **Repositories** (`app/repositories/`): Generic data access layer with filtering, sorting, pagination
- **Services** (`app/services/`): Business logic orchestration and workflow management
- **Routers** (`app/api/v1/`): FastAPI endpoint definitions (14 total modules)
- **Workers** (`app/workers/`): Background jobs for maintenance checks, bulk imports/exports, notifications
- **Utils** (`app/utils/`): Helpers (checksums, sanitization, dynamic filters), export (CSV/Excel), validation

### Database Schema

- **6 PostgreSQL schemas**: master (28 tables), security (9 tables), common (26 tables), infrastructure (2 tables), asset (12 tables), incident (5 tables)
- **58 total tables** with indexes, views, functions, and triggers
- **Alembic migrations** tracked with baseline established for v1.0 frozen schema

## API Endpoints

### Authentication (JWT-based)
- `POST /api/v1/auth/login` - Login with username/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout (invalidate refresh token)

### Users & Permissions
- `GET /api/v1/users` - List users (paginated, admin-only)
- `POST /api/v1/users` - Create user (admin-only)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user (self or admin)
- `DELETE /api/v1/users/{id}` - Delete user (admin-only)

### Master Data
- `GET /api/v1/master/lookups` - List status/category lookup tables
- `POST /api/v1/master/lookups` - Create lookup (admin-only)
- `GET /api/v1/master/specifications` - List specification definitions

### Infrastructure
- `GET /api/v1/infrastructure/locations` - List location hierarchy
- `GET /api/v1/infrastructure/locations/tree` - Get full location tree structure
- `POST /api/v1/infrastructure/locations` - Create location
- `GET /api/v1/infrastructure/locations/{id}/children` - Get child locations
- `GET /api/v1/infrastructure/positions` - List position slots

### Assets (Comprehensive CRUD)
- `GET /api/v1/assets` - List with pagination, filtering, sorting
- `POST /api/v1/assets` - Create new asset
- `GET /api/v1/assets/{id}` - Get asset details
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset
- `GET /api/v1/assets/{id}/specifications` - Asset-specific specifications
- `POST /api/v1/assets/{id}/specifications` - Add specification
- `GET /api/v1/assets/{id}/installations` - Installation history
- `POST /api/v1/assets/{id}/installations` - Record installation
- `GET /api/v1/assets/{id}/movements` - Movement/relocation history
- `POST /api/v1/assets/{id}/movements` - Record movement

### Incidents (Full Lifecycle Management)
- `GET /api/v1/incidents` - List incidents with status/priority filtering
- `POST /api/v1/incidents` - Create new incident
- `GET /api/v1/incidents/{id}` - Get incident with full details
- `PUT /api/v1/incidents/{id}` - Update status, priority, assignment
- `GET /api/v1/incidents/{id}/updates` - Get incident timeline/notes
- `POST /api/v1/incidents/{id}/updates` - Add note to timeline
- `GET /api/v1/incidents/{id}/attachments` - List incident attachments
- `GET /api/v1/work-orders` - List work orders assigned to user
- `POST /api/v1/work-orders` - Create work order for incident
- `GET /api/v1/work-orders/{id}` - Get work order details
- `PUT /api/v1/work-orders/{id}` - Update work order status
- `GET /api/v1/work-orders/{id}/tasks` - Get work order tasks
- `POST /api/v1/work-orders/{id}/tasks` - Create sequenced task
- `PUT /api/v1/work-orders/tasks/{id}` - Complete/update task

### Maintenance (Scheduling & Execution)
- `GET /api/v1/maintenance/checklists` - List maintenance checklists
- `POST /api/v1/maintenance/checklists` - Create checklist template
- `GET /api/v1/maintenance/checklists/{id}/items` - Get checklist items
- `POST /api/v1/maintenance/checklists/{id}/items` - Add item with sequence
- `GET /api/v1/maintenance/schedules` - List maintenance schedules
- `POST /api/v1/maintenance/schedules` - Create recurring schedule
- `GET /api/v1/maintenance/schedules/{id}/history` - Maintenance execution history
- `POST /api/v1/maintenance/history` - Record maintenance completion

### Stock & Inventory
- `GET /api/v1/stock/transactions` - List stock transactions (In/Out/Adjustments)
- `POST /api/v1/stock/transactions` - Record stock transaction
- `GET /api/v1/stock/transactions/{id}` - Get transaction details

### Dashboard & Reporting
- `GET /api/v1/dashboard/summary` - KPI dashboard (total assets, active incidents, overdue maintenance, pending work orders)
- `POST /api/v1/reports/generate` - Generate report (asset summary, incident trends, maintenance compliance)
- `GET /api/v1/search` - Global search across assets, incidents, work orders

### Supporting Endpoints
- `GET /api/v1/health` - API health check
- `GET /api/v1/health/db` - Database connectivity check
- `GET /api/v1/uploads` - File upload/download (future implementation)
- `GET /api/v1/notifications` - In-app notifications (future implementation)

## Testing

### Run Tests
```bash
# All tests
pytest

# Specific module
pytest tests/test_assets.py

# With coverage report
pytest --cov=app tests/

# Verbose output
pytest -v

# Run only async tests
pytest -m asyncio
```

### Test Coverage

- ✓ **test_auth.py**: Login, token refresh/validation, logout flows
- ✓ **test_users.py**: User CRUD, creation, listing operations
- **test_master.py**: Lookup CRUD, specification management
- **test_infrastructure.py**: Location hierarchy, position management, tree API
- **test_assets.py**: Asset CRUD, specifications, installations, movements
- **test_incidents.py**: Incident lifecycle, work orders, task management
- **test_maintenance.py**: Checklists, schedules, execution history
- **test_stock.py**: Stock transactions, ledger, current levels
- **test_permissions.py**: RBAC enforcement, auth requirements, admin operations

### Test Database

- Uses in-memory SQLite for fast tests by default
- Can configure PostgreSQL for integration tests via TEST_DATABASE_URL
- All tests run with async/await patterns using pytest-asyncio

## Development

### Key Patterns Used

**Async-first architecture**:
```python
async def list_assets(session: AsyncSession, skip: int = 0, limit: int = 10):
    return await asset_service.list_assets(session, skip, limit)
```

**Generic repository pattern**:
```python
repo = AssetRepository(Asset, session)
assets = await repo.list(skip=0, limit=10)
```

**Pydantic schemas with ORM mapping**:
```python
class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_name: str
```

**Dependency injection for auth/db**:
```python
@router.get("/assets")
async def list_assets(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
```

### Adding New Features

1. **Define ORM model** in `app/models/` (extends Base, uses `Mapped[]` types)
2. **Create Pydantic schemas** in `app/schemas/` (Base, Create, Update, Read variants)
3. **Implement repository** in `app/repositories/` (extends `BaseRepository[T]`)
4. **Create service** in `app/services/` (orchestrates repository, returns ORM instances)
5. **Add router** in `app/api/v1/{module}/router.py` (uses service, returns Pydantic schemas)
6. **Register router** in `app/api/v1/router.py` (via `include_router()`)
7. **Write tests** in `tests/` (conftest fixtures provide async client)

## Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost/sirms_db
TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:

# Security & JWT
SECRET_KEY=your-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
DEBUG=False
PROJECT_NAME=SIRMS Backend
LOG_LEVEL=INFO
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py                    # Central router registry
│   │       ├── health.py                    # Health checks
│   │       ├── auth/router.py               # Authentication endpoints
│   │       ├── users/router.py              # User management
│   │       ├── master/router.py             # Lookups, specifications
│   │       ├── common/router.py             # Common domain
│   │       ├── infrastructure/router.py     # Locations, positions
│   │       ├── asset/router.py              # Asset management
│   │       ├── incidents/router.py          # Incident management
│   │       ├── maintenance/router.py        # Maintenance operations
│   │       ├── stock/router.py              # Stock transactions
│   │       ├── dashboard/router.py          # KPI dashboard
│   │       ├── reports/router.py            # Report generation
│   │       ├── search/router.py             # Global search
│   │       ├── uploads/router.py            # File uploads
│   │       └── notifications/router.py      # Notifications
│   ├── core/
│   │   ├── config.py                        # Settings/environment
│   │   ├── security.py                      # JWT, password hashing
│   │   ├── exceptions.py                    # Custom exceptions
│   │   ├── logging.py                       # Logging configuration
│   │   ├── pagination.py                    # Pagination helpers
│   │   └── response.py                      # Standard response models
│   ├── db/
│   │   ├── base.py                          # ORM Base class
│   │   ├── database.py                      # Engine, sessionmaker
│   │   └── session.py                       # get_db dependency
│   ├── middleware/
│   │   ├── error_handler.py                 # Exception handling
│   │   ├── logging.py                       # Request/response logging
│   │   └── request_id.py                    # Request ID tracking
│   ├── models/
│   │   ├── __init__.py
│   │   ├── security.py                      # User, Role, Permission models
│   │   ├── master.py                        # Lookup, Specification models
│   │   ├── common.py                        # Common domain models
│   │   ├── infrastructure.py                # Location, Position models
│   │   ├── asset.py                         # Asset, Installation, Movement models
│   │   └── incident.py                      # Incident, WorkOrder, Task models
│   ├── repositories/
│   │   ├── base.py                          # BaseRepository[T] generic CRUD
│   │   ├── security.py                      # User, Role repositories
│   │   ├── master.py                        # Lookup repositories
│   │   ├── common.py                        # Common repositories
│   │   ├── infrastructure.py                # Location repositories
│   │   ├── asset.py                         # Asset, Specification repositories
│   │   ├── incident.py                      # Incident, WorkOrder repositories
│   │   └── maintenance.py                   # Maintenance, Stock repositories
│   ├── schemas/
│   │   ├── auth.py, security.py, master.py, common.py, etc.
│   │   └── Each with Base, Create, Update, Read Pydantic models
│   ├── services/
│   │   ├── auth_service.py                  # Login, token generation
│   │   ├── user_service.py                  # User CRUD, permissions
│   │   ├── master_service.py                # Lookup, Specification CRUD
│   │   ├── asset_service.py                 # Asset workflows
│   │   ├── incident_service.py              # Incident workflows, work orders
│   │   ├── maintenance_service.py           # Maintenance, Stock services
│   │   └── common_service.py                # Common domain logic
│   ├── utils/
│   │   ├── helpers.py                       # Checksums, sanitization, filters, slugs
│   │   ├── export.py                        # CSV/Excel export classes
│   │   └── validation.py                    # Email, phone, URL, custom validators
│   └── workers/
│       ├── base.py                          # BackgroundJob abstract class
│       ├── maintenance_jobs.py              # Overdue checks, archiving
│       ├── import_jobs.py                   # Bulk asset/incident/maintenance imports
│       ├── export_jobs.py                   # CSV/Excel export jobs
│       └── notification_jobs.py             # Notification sending, cleanup, retries
├── tests/
│   ├── conftest.py                          # Pytest fixtures (async client, auth client, db session)
│   ├── test_auth.py                         # ✓ Login, token refresh (passing)
│   ├── test_users.py                        # ✓ User CRUD (passing)
│   ├── test_master.py                       # Lookup, specification tests
│   ├── test_infrastructure.py               # Location hierarchy tests
│   ├── test_assets.py                       # Asset CRUD, specifications, movements
│   ├── test_incidents.py                    # Incident lifecycle, work orders
│   ├── test_maintenance.py                  # Checklists, schedules, history
│   ├── test_stock.py                        # Stock transactions
│   └── test_permissions.py                  # RBAC, authentication
├── alembic/
│   ├── versions/
│   │   └── 001_baseline.py                  # Baseline migration (schema already deployed)
│   └── env.py                               # Migration environment configuration
├── database/
│   ├── ddl/                                 # SQL schemas (extension, master, security, common, infrastructure, asset, incident)
│   ├── seed/                                # Seed data (lookups, templates, samples)
│   ├── validation/                          # Verification scripts
│   ├── deploy.sql                           # Run all DDL and seed scripts
│   ├── redeploy.sql                         # Reset and redeploy
│   └── reset.sql                            # Drop all objects
├── scripts/
│   ├── create_superuser.py                  # CLI: Create admin user
│   └── seed_permissions.py                  # CLI: Sync permission codes to database
├── main.py                                  # FastAPI app entry point
├── pyproject.toml                           # Poetry dependencies (FastAPI, SQLAlchemy, asyncpg, etc.)
└── README.md                                # This file
```

## Dependencies

**Core Framework**:
- FastAPI 0.104+ - Web framework
- Uvicorn - ASGI server
- Pydantic 2.0+ - Data validation
- SQLAlchemy 2.0+ - ORM with async support
- asyncpg - PostgreSQL async driver
- aiosqlite - SQLite async driver (tests)

**Security**:
- python-jose - JWT tokens
- passlib - Password hashing
- bcrypt - Strong hashing

**Database**:
- alembic - Schema migrations
- psycopg2-binary - PostgreSQL driver

**Export**:
- openpyxl - Excel file generation (optional)

**Testing**:
- pytest - Test framework
- pytest-asyncio - Async test support
- httpx - Async HTTP client

See `pyproject.toml` for complete versions and optional dependencies.

## Performance Considerations

- **Async throughout**: All I/O operations are non-blocking
- **Connection pooling**: SQLAlchemy manages pool (default 20 connections)
- **Pagination**: All list endpoints support skip/limit to prevent memory issues
- **Database indexes**: Strategic indexes on foreign keys, status, dates
- **Lazy loading prevention**: Explicit relationship loading in services
- **Query optimization**: Select specific columns when possible

## Security Features

- **JWT Authentication**: Stateless token-based (30-min access, 7-day refresh)
- **Password Security**: bcrypt hashing with salt (passlib/argon2 configurable)
- **RBAC**: Fine-grained permission system (admin-only endpoints protected)
- **Input Validation**: Pydantic validates all request payloads
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM
- **CORS**: Configurable origin-based access (future phase)
- **Rate Limiting**: Can be added via middleware (future phase)

## Future Enhancements

- [ ] **Docker/Kubernetes**: Container orchestration
- [ ] **WebSocket**: Real-time updates and notifications
- [ ] **Elasticsearch**: Full-text search capability
- [ ] **Redis**: Caching layer and sessions
- [ ] **Celery**: Distributed task queue for workers
- [ ] **GraphQL**: Alternative query language
- [ ] **Multi-tenancy**: Organization isolation
- [ ] **Audit logging**: Full change tracking and compliance
- [ ] **API versioning**: Multiple API versions support
- [ ] **OpenAPI/Swagger**: Auto-generated API documentation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Ensure backend installed: `pip install -e ".[dev,export]"` |
| PostgreSQL connection failed | Check DATABASE_URL in .env and ensure PostgreSQL service running |
| Async event loop errors | Use `pytest -p pytest_asyncio` or update conftest.py |
| Permission denied on tests | Run tests with proper AsyncClient from httpx |
| Migration errors | Baseline already stamped; future migrations via `alembic revision --autogenerate` |

## Support

For issues, questions, or feature requests, contact the development team or create an issue in the project repository.

## License

Proprietary - Stock & Infrastructure Resource Management System
