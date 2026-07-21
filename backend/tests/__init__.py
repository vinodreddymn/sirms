"""Test suite for SIRMS backend API.

Covers:
- Master data management (lookups, specifications)
- Infrastructure (locations, positions)
- Asset management (CRUD, specifications, installations, movements)
- Incident management (lifecycle, work orders, tasks)
- Maintenance operations (checklists, schedules, history)
- Stock transactions (CRUD, ledger, transfers)
- Permission and RBAC enforcement
- Authentication and token validation

Run all tests with: pytest
Run specific test file: pytest tests/test_assets.py
Run with coverage: pytest --cov=app tests/
"""
