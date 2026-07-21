# Database Features

## Scope and verification

This document describes the running PostgreSQL database, not just the SQL seed scripts. It was verified by querying the configured `sirms` database as `svr_user` at **2026-07-16 15:03 UTC**.

- Six application schemas with **86 base tables**: `master` (28), `security` (9), `common` (26), `infrastructure` (2), `asset` (16), and `incident` (5).
- **8 views**, **12 functions**, **9 application triggers**, and **244 indexes** are deployed.
- DDL is organised in `database/ddl/`; deployment orchestration is in `database/deploy.sql`.

## Live operational data

The following records currently exist in the database. These values prove that the database has application data as well as reference/seed data.

| Area | Live records |
| --- | ---: |
| Users, roles, user-role assignments | 8, 3, 3 |
| Refresh tokens and notification preferences | 13, 3 |
| Customers, projects, vendors | 1, 1, 1 |
| Locations and position slots | 29, 14 |
| Assets, specifications, installations, movements | 3, 5, 3, 2 |
| Asset relationships and stock transactions | 1, 2 |
| Maintenance checklists, checklist items, schedules | 1, 3, 1 |
| Incidents, updates, work orders, work-order tasks | 1, 1, 1, 2 |

Maintenance history, documents, photos, attachments, notifications, audit/activity logs, imports, exports, saved searches/reports, tags, and QR/barcode histories are currently empty.

## Implemented domains

### Master data

- Asset taxonomy: categories, subcategories, manufacturers, and models.
- Asset status, condition, lifecycle, maintenance types, movement types, and stock transaction types.
- Incident status, priority, category, failure/root-cause categories, and work-order status.
- Location/position types and templates, project types, document/photo/relationship types, role templates.
- Dynamic asset specification definitions, including supported data type, unit, required flag, display order, and category/subcategory applicability.

### Security and common services

- Users, roles, permissions, role assignments, login history, password-reset tokens, refresh tokens, and API tokens.
- Customers, projects, vendors, file attachments, audit/activity records, notifications and preferences.
- Dashboard preferences, saved searches/filters/reports, report definitions, comments, tags, favourites/watch lists, import/export tracking, QR/barcode history, and business number sequences.

### Infrastructure, assets, and incidents

- A hierarchical location tree with optional geographic coordinates and position slots with capacity.
- Asset register with project, classification, lifecycle/status/condition, specification values, installation history, movements, relationships, documents, and photos.
- Stock transaction ledger tied to projects, assets, and locations.
- Maintenance checklists, checklist items, recurring schedules, and execution history.
- Incidents, incident updates, attachments, work orders, and sequenced work-order tasks.
- O&M asset operations: installed/spare role, manual health rating, network configuration, repair history, replacement history, immutable timeline events, and field notes.

## Database automation and reporting structures

- Business-number generation and generic updated-at maintenance.
- Location-path resolution and location/position creation from templates.
- Asset specification validation, installation capacity validation, and synchronization of an asset's current location from its installation.
- Next-maintenance-date calculation.
- Views for location hierarchy, asset register/current location/history/maintenance due, incident summary/open work orders, and dashboard summary.

## Important status notes

- The database supports more domains than are currently exposed in the frontend.
- The live operational records above may have originated through prior API/manual activity; this assessment intentionally does not classify them as seed-only.
- The deployment script loads sample data after DDL. It is intended for a fresh database; it refuses to deploy into non-empty application schemas.
