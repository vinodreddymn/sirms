# Backend Features

## Architecture

The backend is a FastAPI application using async SQLAlchemy and PostgreSQL. It follows a router -> service -> repository -> ORM model structure, with Pydantic request/response schemas. The application is mounted below `/api/v1` and has CORS, request IDs, request logging, standard JSON responses, validation handling, and database-session cleanup.

## Implemented API capabilities

### Access and user management

- JWT login, refresh, logout, logout-from-all-sessions, password change, and current-user retrieval.
- User create, list, read, update, and delete operations.
- Role/permission-aware dependencies are present for protected operations.

### Master, common, and infrastructure data

- Generic list/create/read/update endpoints for supported master lookup tables.
- List/create/update dynamic asset specification definitions.
- Customer, project, and vendor list/create/read/update endpoints.
- Location tree, paginated list, search, create/read/update, and location positions create/list/update.

### Asset and inventory workflows

- Asset summary, filtered/paginated/sorted asset register, create/read/update, and CSV export. Asset deletion is deliberately blocked so records remain permanent.
- Asset specification definitions and asset-specific specification records.
- Installation and movement history read/create operations.
- Stock transaction list/create/read operations.
- Repair-history and field-note recording, chronological asset timeline retrieval, and an atomic asset-replacement endpoint that transfers the installation to a spare, updates both operational states, records movements, and preserves replacement/timeline history.

### Incident and maintenance workflows

- Incident list/create/read/update, timeline updates, and attachment records.
- Work-order list/create/read/update and work-order task list/create/update.
- Maintenance checklist and item list/create/read/update, schedule list/create/read/update, and maintenance-history list/create endpoints.

### Supporting services

- Dashboard API: live counts for total assets, active incidents, overdue maintenance, and unfinished work orders; per-user dashboard preferences.
- Reports API: generate JSON report data and export CSV/XLSX for asset register, incidents, maintenance history, work orders, and asset movements (up to 5,000 records).
- Upload API: validates configured maximum size, sanitizes filename, stores the file, records metadata/checksum, and supports metadata/download retrieval.
- Notification API: current-user list, unread count, mark-read, and read/update preferences.
- Health and database reachability checks.

## Known incomplete or limited backend features

- Global search currently always returns an empty result set.
- Background maintenance, import, export, and notification jobs are scaffolded but return stub counts; no scheduler/queue integration is registered.
- Report generation/export exists synchronously, but report persistence and PDF output are not implemented.
- Files can be uploaded and downloaded, but asset/incident attachment association flows are not exposed as a dedicated upload-to-entity workflow.
- Notification records and preferences are supported; delivery/retry processing is still stubbed.

## Validation and tests

- Test modules cover authentication, users, permissions, master data, infrastructure, assets, incidents, maintenance, and stock.
- Tests default to an in-memory SQLite database, while production configuration targets PostgreSQL through `asyncpg`.

## Main source locations

- Route registration: `backend/app/api/v1/router.py`
- API endpoint modules: `backend/app/api/v1/`
- Domain logic: `backend/app/services/`
- Database access: `backend/app/repositories/` and `backend/app/models/`
