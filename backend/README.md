# ARIMS / SIRMS Backend

FastAPI backend scaffold for the frozen ARIMS / SIRMS PostgreSQL Version 1.0 database.

## Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,export]"
```

## Run

```powershell
uvicorn main:app --reload
```

Health checks:

- `GET /api/v1/health`
- `GET /api/v1/health/db`

## Current Scope

This scaffold includes project configuration, settings, security helpers, logging, middleware, database session management, response helpers, pagination helpers, and health routes.

Next implementation steps are ORM models, repositories, services, authentication routes, and module APIs.
