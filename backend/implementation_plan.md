ARIMS / SIRMS — FastAPI Backend Implementation Plan
Goal
Implement a production-ready FastAPI backend (Version 1.0) that fully exposes every capability of the frozen PostgreSQL v1.0 database. The backend follows a layered architecture (Router → Service → Repository → ORM) with JWT authentication, database-driven RBAC, and comprehensive API documentation.

Database Contract Summary
The backend must map 58 tables across 6 schemas, 8 views, 13 functions/triggers, and 74 indexes.

Schema	Tables	Key Entities
master	28	Lookups, templates, specification definitions, transaction types
security	9	Users, roles, permissions, tokens, login history
common	26	Customers, projects, vendors, attachments, audit/activity logs, notifications, imports/exports, comments, tags, favorites, watch list, number sequences
infrastructure	2	Locations (unlimited hierarchy), location positions
asset	12	Assets, specifications, installations, movements, stock, documents, photos, relationships, maintenance checklists/schedules/history
incident	5	Incidents, updates, work orders, tasks, attachments
User Review Required
IMPORTANT

Password hashing: The spec lists Argon2 (preferred) or bcrypt. This plan uses Argon2 via argon2-cffi. Please confirm, or specify bcrypt.

IMPORTANT

File storage: The database stores file metadata (common.attachments) with file_path. This plan implements local filesystem storage under a configurable UPLOAD_DIR. If you need S3/MinIO/Azure Blob integration, please specify.

IMPORTANT

Email/SMS delivery: Notification channels beyond IN_APP are marked "future" in the spec. This plan creates the notification service with an IN_APP implementation and abstract interfaces for EMAIL/SMS/PUSH that raise NotImplementedError. Confirm this approach.

WARNING

Database migration strategy: The database is already deployed via raw DDL scripts. Alembic will be configured with --autogenerate disabled — instead using a stamped baseline migration that matches the current v1.0 schema. Future schema changes will be hand-written Alembic migrations. Confirm this approach.

Open Questions
IMPORTANT

CORS origins: What frontend URL(s) should be whitelisted? (e.g., http://localhost:3000 for dev, production domain). For now, the plan uses a configurable CORS_ORIGINS env var.

IMPORTANT

JWT token lifetimes: The plan proposes 30 minutes for access tokens and 7 days for refresh tokens. Are these acceptable?

IMPORTANT

Rate limiting: Should login and API endpoints have rate limiting? If yes, this plan can add slowapi. Not included by default.

NOTE

Profile photo: The security.users table does not have a profile_photo column. The spec mentions "Profile photo" under User Management. This plan will handle profile photos via common.attachments linked to the user entity through the generic entity_name/entity_id pattern (similar to comments/tags). Confirm or suggest an alternative.

Current implementation status
- [x] Phase 1 — Project Foundation: app factory, middleware, and API router structure
- [x] Phase 2 — Core Configuration: settings, security helpers, exceptions, pagination, and logging
- [x] Phase 3 — Database Connection: async SQLAlchemy engine and session dependency
- [x] Phase 4 — ORM Models: core security, master, common, infrastructure, asset, and incident models created
- [x] Phase 5 — Schemas: auth, security, master, common, infrastructure, asset, incident, dashboard, reports, search, uploads, notifications
- [x] Phase 6 — Repositories: base, security, master, common, infrastructure, asset, incident, maintenance repositories
- [x] Phase 7 — Services: auth, user, master, common, infrastructure, asset, incident, maintenance, stock services
- [x] Phase 8 — Dependencies/Middleware: auth dependency, request ID, logging, and error middleware are present
- [x] Phase 9 — API routers: health, auth, users, master, common, infrastructure, asset, incidents, maintenance, stock, dashboard, reports, search, uploads, notifications
- [x] Phase 10 — Alembic baseline: baseline migration and env.py configuration
- [x] Phase 11 — Workers: background job infrastructure with maintenance, import, export, and notification workers
- [x] Phase 12 — Utilities: helpers, export (CSV/Excel), and validation functions
- [x] Phase 13 — Tests: comprehensive test suite with conftest fixtures, test database setup, and 8 test modules
- [x] Phase 14 — Documentation & Scripts: comprehensive README, create_superuser.py, seed_permissions.py

Proposed Changes
The entire backend will be created under c:\Users\DELL\Documents\AI_Projects\sirms\backend\. The implementation follows the 20-step development sequence from the spec.

Phase 1 — Project Foundation
[NEW] 
pyproject.toml
Project metadata and dependencies:

Core: fastapi[standard], uvicorn[standard], sqlalchemy[asyncio], asyncpg, pydantic[email], pydantic-settings
Auth: python-jose[cryptography], argon2-cffi, python-multipart
Migration: alembic
Utils: structlog, python-dateutil, orjson
Dev/Test: pytest, pytest-asyncio, httpx, factory-boy, coverage
Export: openpyxl (Excel), csv (stdlib)
[NEW] 
.env.example
Template for all environment variables with safe defaults.

[MODIFY] 
.env
Extend with JWT secrets, token lifetimes, upload dir, CORS origins, log level.

[NEW] 
app/__init__.py
Package marker.

[NEW] 
main.py
FastAPI application factory:

Lifespan handler for DB connection pool startup/shutdown
Include all API routers under /api/v1
Register middleware (CORS, request ID, logging, error handling)
OpenAPI metadata (title, description, version, tags)
Phase 2 — Core Configuration & Infrastructure
[NEW] 
app/core/config.py
Settings class using pydantic-settings:

DATABASE_URL (assembled from host/port/name/user/password)
SECRET_KEY, JWT_ALGORITHM (HS256), ACCESS_TOKEN_EXPIRE_MINUTES (30), REFRESH_TOKEN_EXPIRE_DAYS (7)
CORS_ORIGINS, UPLOAD_DIR, MAX_UPLOAD_SIZE_MB
LOG_LEVEL, LOG_FORMAT
APP_NAME, APP_VERSION, API_V1_PREFIX
[NEW] 
app/core/security.py
hash_password(plain) → Argon2 hash
verify_password(plain, hash) → bool
create_access_token(data, expires_delta) → JWT string
create_refresh_token(data, expires_delta) → JWT string
decode_token(token) → payload dict or raise
[NEW] 
app/core/logging.py
structlog configuration:

JSON output in production, colored console in dev
Bind request_id, user_id, method, path per-request
Filter sensitive fields (password, token)
[NEW] 
app/core/exceptions.py
Custom exception hierarchy:

AppException(status_code, message, errors)
NotFoundException, ConflictException, ForbiddenException, ValidationException, UnauthorizedException
[NEW] 
app/core/response.py
Standard response envelope:

python

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    errors: list[ErrorDetail] | None = None
    timestamp: datetime
    request_id: str
[NEW] 
app/core/pagination.py
PaginationParams(page, page_size, sort, order, search) — injectable dependency
PaginatedResponse(items, total, page, page_size, pages)
Phase 3 — Database Connection
[NEW] 
app/db/database.py
Async SQLAlchemy engine (create_async_engine with asyncpg)
Connection pool configuration (pool_size=10, max_overflow=20)
async_session_factory using async_sessionmaker
[NEW] 
app/db/session.py
get_db() async generator dependency for request-scoped sessions
Transaction management (commit on success, rollback on error)
[NEW] 
app/db/base.py
Base = declarative_base() with MetaData naming conventions
AuditMixin mixin: created_at, created_by, updated_at, updated_by, is_active
Import all models for Alembic auto-detection
Phase 4 — ORM Models (All 58 Tables)
All models use SQLAlchemy 2.x Mapped[] / mapped_column() syntax with type annotations.

[NEW] 
app/models/master.py
28 models mapping every master.* table:

Lookup tables (18): LocationType, PositionType, AssetCategory, AssetCondition, AssetStatus, AssetLifecycle, MaintenanceType, FailureCategory, RootCauseCategory, IncidentStatus, IncidentPriority, IncidentCategory, WorkOrderStatus, RelationshipType, DocumentType, PhotoType, ProjectType, UserRoleTemplate, MovementType
All share a MasterLookupBase mixin: id: BIGSERIAL, code, name, description, display_order, is_active, audit cols
Template tables (4): LocationTemplate, LocationTemplateNode, PositionTemplate, PositionTemplateNode
Specialized: AssetSubcategory (FK → category), Manufacturer, AssetModel (FK → manufacturer, subcategory), SpecificationDefinition (FK → category, subcategory, data_type CHECK), StockTransactionType (quantity_effect)
[NEW] 
app/models/security.py
9 models:

User (UUID PK, username, email, password_hash, is_locked, default_project_id FK)
Role (UUID PK, role_code, role_name, is_system_role, role_template_id FK)
Permission (UUID PK, permission_code, permission_name, module_name)
RolePermission (bridge: role_id + permission_id, composite unique)
UserRole (bridge: user_id + role_id + project_id, date range)
LoginHistory (user_id, login_status CHECK, ip_address, device_info)
PasswordResetToken (user_id, token_hash, expires_at, used_at)
RefreshToken (user_id, token_hash, issued_at, expires_at, revoked_at)
ApiToken (user_id, token_name, token_hash, scope_json, expires_at, revoked_at)
[NEW] 
app/models/common.py
26 models:

Customer, Project (FK → customer, project_type), Vendor (vendor_type CHECK)
Attachment, AuditLog, ActivityLog, Notification, SystemSetting
DashboardPreference, SavedSearch, SavedFilter
ReportDefinition, SavedReport
QrGenerationHistory, QrPrintHistory, BarcodeHistory
ImportJob, ImportError, ExportHistory
Comment, Tag, EntityTag
FavoriteAsset, WatchList
NotificationPreference, NumberSequence
[NEW] 
app/models/infrastructure.py
2 models:

Location (UUID PK, self-referencing parent_location_id, project_id FK, location_type_id FK, GIS fields, composite unique on project+code)
LocationPosition (UUID PK, location_id FK, position_type_id FK, maximum_capacity, composite unique)
[NEW] 
app/models/asset.py
12 models:

Asset (UUID PK, asset_number UNIQUE, multiple FK to master lookups, current_location_id)
AssetSpecification (asset_id + spec_def_id composite unique, typed value columns)
AssetInstallation (asset_id, location_position_id, installed_on/removed_on, current_flag)
AssetMovement (asset_id, movement_type_id, from/to location, vendor, CHECK constraint)
StockTransaction (project_id, asset_id, type_id, location, vendor, quantity)
AssetDocument, AssetPhoto (FK to attachments)
AssetRelationship (self-referencing with CHECK asset_id ≠ related_asset_id)
MaintenanceChecklist, ChecklistItem
MaintenanceSchedule, MaintenanceHistory
[NEW] 
app/models/incident.py
5 models:

Incident (UUID PK, incident_number UNIQUE, project/asset/location/priority/status FKs)
IncidentUpdate (incident_id FK, status_after_update_id FK)
WorkOrder (UUID PK, work_order_number UNIQUE, incident_id FK, status FK)
WorkOrderTask (work_order_id FK, task_sequence, composite unique)
IncidentAttachment (incident_id + attachment_id, category CHECK)
[NEW] 
app/models/__init__.py
Re-export all models for Alembic and dependency injection.

Phase 5 — Pydantic Schemas
Each module gets a dedicated schema file with Create, Update, Read, List, and Filter variants.

[NEW] 
app/schemas/master.py
LookupCreate / LookupUpdate / LookupRead — reusable base for all 18 lookup tables
Specialized schemas for AssetSubcategory, AssetModel, SpecificationDefinition, StockTransactionType
Template schemas: LocationTemplateRead (with nested nodes), PositionTemplateRead (with nested nodes)
[NEW] 
app/schemas/security.py
UserCreate, UserUpdate, UserRead, UserListRead
RoleCreate, RoleUpdate, RoleRead (with permissions list)
PermissionRead
UserRoleAssign, UserRoleRead
LoginHistoryRead
[NEW] 
app/schemas/auth.py
LoginRequest (username, password)
TokenResponse (access_token, refresh_token, token_type, expires_in)
RefreshTokenRequest
PasswordChangeRequest (old_password, new_password)
PasswordResetRequest, PasswordResetConfirm
ApiTokenCreate, ApiTokenRead
[NEW] 
app/schemas/common.py
Customer CRUD schemas
Project CRUD schemas
Vendor CRUD schemas
Attachment, Comment, Tag, Notification schemas
Import/Export schemas
System settings, dashboard preferences, saved searches/filters
[NEW] 
app/schemas/infrastructure.py
LocationCreate, LocationUpdate, LocationRead, LocationTreeNode (recursive)
LocationPositionCreate, LocationPositionRead
LocationFromTemplateRequest (template_id, code_prefix, name_prefix)
[NEW] 
app/schemas/asset.py
AssetCreate, AssetUpdate, AssetRead, AssetDetailRead (with specs, location, relationships)
AssetSpecificationCreate, AssetSpecificationRead
AssetInstallationCreate, AssetInstallationRead
AssetMovementCreate, AssetMovementRead
StockTransactionCreate, StockTransactionRead
AssetDocumentCreate, AssetPhotoCreate
AssetRelationshipCreate
Maintenance schemas: checklist, schedule, history
[NEW] 
app/schemas/incident.py
IncidentCreate, IncidentUpdate, IncidentRead, IncidentDetailRead
IncidentUpdateCreate (timeline entry)
WorkOrderCreate, WorkOrderUpdate, WorkOrderRead
WorkOrderTaskCreate, WorkOrderTaskRead
[NEW] 
app/schemas/dashboard.py
DashboardSummary, KPIResponse, ChartDataResponse
[NEW] 
app/schemas/reports.py
ReportRequest, ReportResponse, ExportRequest
[NEW] 
app/schemas/search.py
GlobalSearchRequest, GlobalSearchResponse, SearchResultItem
Phase 6 — Repository Layer
Every repository follows a consistent pattern: inject AsyncSession, return ORM model instances, use select() with eager/lazy loading strategies.

[NEW] 
app/repositories/base.py
Generic BaseRepository[T]:

get_by_id(id), get_all(pagination), create(data), update(id, data), soft_delete(id), hard_delete(id)
count(filters), exists(filters)
Filter/sort/search builder
Handles both BIGSERIAL and UUID primary keys
[NEW] 
app/repositories/master.py
LookupRepository — generic for all 18 standard lookup tables
AssetSubcategoryRepository, AssetModelRepository, SpecificationDefinitionRepository
LocationTemplateRepository, PositionTemplateRepository (with node loading)
[NEW] 
app/repositories/security.py
UserRepository — get_by_username, get_by_email, get_with_roles_and_permissions
RoleRepository — get_with_permissions
PermissionRepository
UserRoleRepository
RefreshTokenRepository, LoginHistoryRepository, ApiTokenRepository
[NEW] 
app/repositories/common.py
CustomerRepository, ProjectRepository, VendorRepository
AttachmentRepository, CommentRepository, TagRepository
NotificationRepository, AuditLogRepository, ActivityLogRepository
ImportJobRepository, ExportHistoryRepository
NumberSequenceRepository (calls common.next_sequence_value() via raw SQL)
[NEW] 
app/repositories/infrastructure.py
LocationRepository — get_tree, get_children, get_path (calls infrastructure.get_location_path()), move_location, search
LocationPositionRepository — get_by_location, check_occupancy
Template creation wrappers (calls infrastructure.create_location_from_template())
[NEW] 
app/repositories/asset.py
AssetRepository — search, filter by status/category/location/project, bulk operations
AssetSpecificationRepository, AssetInstallationRepository
AssetMovementRepository, StockTransactionRepository
AssetDocumentRepository, AssetPhotoRepository, AssetRelationshipRepository
MaintenanceChecklistRepository, MaintenanceScheduleRepository, MaintenanceHistoryRepository
[NEW] 
app/repositories/incident.py
IncidentRepository — search, filter, with timeline loading
IncidentUpdateRepository
WorkOrderRepository, WorkOrderTaskRepository
IncidentAttachmentRepository
Phase 7 — Service Layer
Business rules, validation, orchestration, and audit logging live here.

[NEW] 
app/services/auth_service.py
login(username, password) — verify credentials, check locked, create tokens, record login history
logout(user_id, refresh_token) — revoke refresh token
refresh_token(token) — validate, rotate, issue new pair
change_password(user_id, old, new) — verify old, enforce policy, update hash
request_password_reset(email) — generate token, (future: send email)
confirm_password_reset(token, new_password) — validate token, update hash
create_api_token(user_id, name, scope) / revoke_api_token(token_id)
[NEW] 
app/services/user_service.py
User CRUD with duplicate username/email checks
Role assignment/removal (with project scope)
Profile update, lock/unlock
Notification preferences management
[NEW] 
app/services/master_service.py
Generic lookup CRUD (code uniqueness enforcement)
Template management with nested node CRUD
Specification definition management
[NEW] 
app/services/customer_service.py
Customer CRUD with code uniqueness
Customer contacts management
[NEW] 
app/services/project_service.py
Project CRUD with customer validation
Project activation/deactivation
Number sequence initialization
[NEW] 
app/services/vendor_service.py
Vendor CRUD with type validation
Vendor history tracking
[NEW] 
app/services/infrastructure_service.py
Location CRUD with hierarchy validation (prevent circular references)
Location tree building (recursive)
Location path retrieval
Location move (re-parent with descendant validation)
Template-based location creation (delegates to DB function)
Position CRUD with capacity validation
Bulk position creation from templates
[NEW] 
app/services/asset_service.py
Asset CRUD with auto-generated asset_number (via common.generate_business_number)
Asset installation (validate capacity via infrastructure.validate_installation_capacity)
Asset removal (set current_flag=FALSE, removed_on)
Asset movement tracking
Asset transfer between locations
Specification management (validate data_type match)
Document and photo management (with attachment creation)
QR code / barcode generation and history
Asset relationship management (prevent self-reference)
Lifecycle transitions
Bulk import/export orchestration
[NEW] 
app/services/stock_service.py
Stock transaction creation with quantity effect application
Stock ledger queries (current stock by location/project)
Movement history
Receive, issue, transfer, repair, OEM, scrap, adjustment workflows
[NEW] 
app/services/incident_service.py
Incident CRUD with auto-generated incident_number
Assignment (update assigned_to, create timeline entry, notify)
Status transitions (validate lifecycle: OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED)
Timeline management
Watch list management
Comment management
Attachment management
Close incident (set closed_date)
[NEW] 
app/services/workorder_service.py
Work order CRUD with auto-generated work_order_number
Task management (sequence ordering)
Status transitions (PLANNED → RELEASED → IN_PROGRESS → COMPLETED/CANCELLED)
Assignment, scheduling, completion
[NEW] 
app/services/maintenance_service.py
Checklist management (with items)
Schedule management (calculate next_due_date via DB function)
Execution recording (create history, update schedule next_due_date)
Overdue detection
Calendar view data
[NEW] 
app/services/dashboard_service.py
Aggregate KPIs from common.vw_dashboard_summary
Asset count by status, category, lifecycle
Incident count by status, priority
Maintenance due summary
Work order summary
Recent activities (from common.activity_logs)
Chart data aggregation
[NEW] 
app/services/report_service.py
Asset register report
Incident register report
Maintenance history report
Work order report
Downtime analysis
Asset movement report
Vendor performance report
Export to CSV / Excel (using openpyxl)
Report definition and saved report management
[NEW] 
app/services/search_service.py
Global search across assets, locations, incidents, projects, work orders, users
Saved search management
Saved filter management
Module-specific search with advanced filtering
[NEW] 
app/services/upload_service.py
File upload (validate type, size, compute checksum)
Attachment metadata creation
File retrieval / streaming
Version tracking
[NEW] 
app/services/notification_service.py
Create in-app notification
Mark as read
Get unread count
Notification preferences management
Abstract interfaces for EMAIL/SMS/PUSH (future)
Watch list notifications
Assignment notifications
Maintenance due notifications
[NEW] 
app/services/audit_service.py
Audit log creation (schema, table, record, action, old/new data)
Activity log creation (module, entity, type, details)
Query audit trail for entity
Phase 8 — Dependencies & Middleware
[NEW] 
app/dependencies/auth.py
get_current_user — decode JWT, load user from DB
get_current_active_user — ensure not locked/inactive
require_permission(permission_code) — check user's roles → permissions
require_any_permission(*codes) / require_all_permissions(*codes)
get_optional_user — for public endpoints
[NEW] 
app/dependencies/project.py
get_current_project(project_id: UUID | None) — resolve from header or user default
Project-scoped data filtering
[NEW] 
app/middleware/request_id.py
Generate UUID request ID, attach to response header, bind to structlog context
[NEW] 
app/middleware/logging.py
Log request method, path, status code, duration
Skip health check endpoints
[NEW] 
app/middleware/error_handler.py
Catch AppException → return ApiResponse with proper status code
Catch ValidationError → 422 with field-level errors
Catch unhandled → 500 with generic message (log full trace)
Phase 9 — API Routers
All routers follow the pattern: inject dependencies, call service, wrap in ApiResponse.

[NEW] 
app/api/v1/auth/router.py
Method	Path	Description
POST	/auth/login	Login
POST	/auth/logout	Logout (revoke refresh token)
POST	/auth/refresh	Refresh token pair
GET	/auth/me	Current user profile
POST	/auth/change-password	Change password
POST	/auth/forgot-password	Request reset
POST	/auth/reset-password	Confirm reset
POST	/auth/api-tokens	Create API token
GET	/auth/api-tokens	List API tokens
DELETE	/auth/api-tokens/{id}	Revoke API token
[NEW] 
app/api/v1/users/router.py
Method	Path	Description
GET	/users	List users (paginated)
POST	/users	Create user
GET	/users/{id}	Get user detail
PUT	/users/{id}	Update user
DELETE	/users/{id}	Deactivate user
POST	/users/{id}/roles	Assign role
DELETE	/users/{id}/roles/{role_id}	Remove role
GET	/users/{id}/permissions	Get effective permissions
GET	/users/{id}/login-history	Login history
PUT	/users/{id}/notification-preferences	Update notification prefs
[NEW] 
app/api/v1/master/router.py
Generic CRUD endpoints for all lookup tables, driven by a factory pattern:

Method	Path	Description
GET	/master/{table_name}	List all items
POST	/master/{table_name}	Create item
GET	/master/{table_name}/{id}	Get by ID
PUT	/master/{table_name}/{id}	Update
DELETE	/master/{table_name}/{id}	Soft delete
Plus dedicated endpoints for templates and specification definitions:

Method	Path	Description
GET	/master/location-templates	List templates with nodes
POST	/master/location-templates	Create template with nodes
GET	/master/position-templates	List templates with nodes
POST	/master/position-templates	Create template with nodes
GET	/master/specification-definitions	List (filterable by subcategory)
POST	/master/specification-definitions	Create
[NEW] 
app/api/v1/common/router.py
Customers CRUD: /customers
Projects CRUD: /projects
Vendors CRUD: /vendors
Tags CRUD: /tags
Comments: /comments (entity-scoped)
System settings: /settings
[NEW] 
app/api/v1/infrastructure/router.py
Method	Path	Description
GET	/locations	List locations (flat, paginated)
GET	/locations/tree	Location hierarchy tree
POST	/locations	Create location
POST	/locations/from-template	Create from template
GET	/locations/{id}	Get location detail
GET	/locations/{id}/path	Get full path string
GET	/locations/{id}/children	Get direct children
PUT	/locations/{id}	Update location
PUT	/locations/{id}/move	Move to new parent
DELETE	/locations/{id}	Soft delete
GET	/locations/{id}/positions	List positions
POST	/locations/{id}/positions	Create position
POST	/locations/{id}/positions/from-template	Create from position template
PUT	/positions/{id}	Update position
DELETE	/positions/{id}	Soft delete position
[NEW] 
app/api/v1/assets/router.py
Method	Path	Description
GET	/assets	List/search assets (paginated)
POST	/assets	Create asset
GET	/assets/{id}	Get asset detail (with specs, location, relationships)
PUT	/assets/{id}	Update asset
DELETE	/assets/{id}	Soft delete
GET	/assets/{id}/specifications	Get specifications
PUT	/assets/{id}/specifications	Upsert specifications
POST	/assets/{id}/install	Install at position
POST	/assets/{id}/remove	Remove from position
POST	/assets/{id}/move	Move to location
POST	/assets/{id}/transfer	Transfer between locations
GET	/assets/{id}/movements	Movement history
GET	/assets/{id}/installations	Installation history
GET	/assets/{id}/documents	List documents
POST	/assets/{id}/documents	Add document
GET	/assets/{id}/photos	List photos
POST	/assets/{id}/photos	Add photo
GET	/assets/{id}/relationships	List relationships
POST	/assets/{id}/relationships	Add relationship
DELETE	/assets/{id}/relationships/{rel_id}	Remove relationship
GET	/assets/{id}/timeline	Full asset history
GET	/assets/{id}/qr-code	Generate/get QR
POST	/assets/bulk-import	Bulk import
GET	/assets/bulk-export	Bulk export
POST	/assets/{id}/favorite	Add to favorites
DELETE	/assets/{id}/favorite	Remove from favorites
[NEW] 
app/api/v1/maintenance/router.py
Method	Path	Description
GET	/maintenance/checklists	List checklists
POST	/maintenance/checklists	Create checklist with items
GET	/maintenance/checklists/{id}	Get with items
PUT	/maintenance/checklists/{id}	Update
GET	/maintenance/schedules	List schedules
POST	/maintenance/schedules	Create schedule
GET	/maintenance/schedules/{id}	Get schedule
PUT	/maintenance/schedules/{id}	Update schedule
GET	/maintenance/schedules/due	Get overdue/upcoming
GET	/maintenance/schedules/calendar	Calendar view
POST	/maintenance/history	Record execution
GET	/maintenance/history	List history
GET	/maintenance/history/{id}	Get history detail
[NEW] 
app/api/v1/incidents/router.py
Method	Path	Description
GET	/incidents	List/search incidents
POST	/incidents	Create incident
GET	/incidents/{id}	Get detail with timeline
PUT	/incidents/{id}	Update incident
POST	/incidents/{id}/assign	Assign to user
POST	/incidents/{id}/close	Close incident
GET	/incidents/{id}/updates	Get timeline
POST	/incidents/{id}/updates	Add timeline entry
GET	/incidents/{id}/attachments	List attachments
POST	/incidents/{id}/attachments	Add attachment
POST	/incidents/{id}/watch	Add to watch list
DELETE	/incidents/{id}/watch	Remove from watch list
GET	/incidents/{id}/comments	List comments
POST	/incidents/{id}/comments	Add comment
[NEW] 
app/api/v1/workorders/router.py
Method	Path	Description
GET	/work-orders	List work orders
POST	/work-orders	Create work order
GET	/work-orders/{id}	Get with tasks
PUT	/work-orders/{id}	Update
GET	/work-orders/{id}/tasks	List tasks
POST	/work-orders/{id}/tasks	Add task
PUT	/work-orders/{id}/tasks/{task_id}	Update task
DELETE	/work-orders/{id}/tasks/{task_id}	Remove task
[NEW] 
app/api/v1/dashboard/router.py
Method	Path	Description
GET	/dashboard/summary	Overall KPIs
GET	/dashboard/assets/by-status	Asset counts by status
GET	/dashboard/assets/by-category	Asset counts by category
GET	/dashboard/incidents/by-status	Incident counts by status
GET	/dashboard/incidents/by-priority	Incident counts by priority
GET	/dashboard/maintenance/due	Maintenance due summary
GET	/dashboard/work-orders/summary	Work order summary
GET	/dashboard/recent-activities	Recent activity feed
GET	/dashboard/preferences	Get user preferences
PUT	/dashboard/preferences	Update user preferences
[NEW] 
app/api/v1/reports/router.py
Method	Path	Description
GET	/reports/asset-register	Asset register report
GET	/reports/incident-register	Incident register report
GET	/reports/maintenance-history	Maintenance history report
GET	/reports/work-orders	Work order report
GET	/reports/asset-movements	Asset movement report
GET	/reports/downtime	Downtime analysis
GET	/reports/vendor-performance	Vendor performance
POST	/reports/export	Export report (CSV/Excel)
GET	/reports/definitions	List report definitions
POST	/reports/saved	Save a report
GET	/reports/saved	List saved reports
[NEW] 
app/api/v1/search/router.py
Method	Path	Description
GET	/search	Global search
GET	/search/saved	List saved searches
POST	/search/saved	Save a search
GET	/search/filters	List saved filters
POST	/search/filters	Save a filter
[NEW] 
app/api/v1/uploads/router.py
Method	Path	Description
POST	/uploads	Upload file(s)
GET	/uploads/{id}	Get attachment metadata
GET	/uploads/{id}/download	Stream file
DELETE	/uploads/{id}	Soft delete
[NEW] 
app/api/v1/notifications/router.py
Method	Path	Description
GET	/notifications	List user notifications
GET	/notifications/unread-count	Unread count
PUT	/notifications/{id}/read	Mark as read
PUT	/notifications/read-all	Mark all as read
GET	/notifications/preferences	Get preferences
PUT	/notifications/preferences	Update preferences
[NEW] 
app/api/v1/stock/router.py
Method	Path	Description
POST	/stock/receive	Receive stock
POST	/stock/issue	Issue stock
POST	/stock/transfer	Transfer stock
POST	/stock/repair	Send to repair
POST	/stock/scrap	Scrap stock
POST	/stock/adjustment	Stock adjustment
GET	/stock/ledger	Stock ledger
GET	/stock/current	Current stock
GET	/stock/movements	Movement history
Phase 10 — Alembic Setup
[NEW] 
alembic.ini
[NEW] 
alembic/env.py
[NEW] 
alembic/versions/001_baseline.py
Empty migration stamped as baseline (DDL already applied)
Future migrations are hand-written
Phase 11 — Background Jobs
[NEW] 
app/workers/__init__.py
[NEW] 
app/workers/base.py
Abstract BackgroundJob interface (swappable with Celery later).

[NEW] 
app/workers/maintenance_jobs.py
Check overdue maintenance, create notifications
[NEW] 
app/workers/import_jobs.py
Process bulk import files
[NEW] 
app/workers/export_jobs.py
Generate export files (CSV, Excel)
[NEW] 
app/workers/notification_jobs.py
Send queued notifications
Phase 12 — Utilities
[NEW] 
app/utils/helpers.py
generate_checksum(file), sanitize_filename(), format_datetime()
build_filter_query(), apply_sorting()
[NEW] 
app/utils/export.py
CSV writer, Excel writer (openpyxl)
Phase 13 — Tests
[NEW] 
tests/conftest.py
Test database setup (async test session)
Fixtures: test client, authenticated client, test user, test project, test data factories
[NEW] 
tests/test_auth.py
Login success/failure, token refresh, password change, account locking
[NEW] 
tests/test_users.py
CRUD, role assignment, permission checks
[NEW] 
tests/test_master.py
Lookup CRUD, template CRUD, specification definitions
[NEW] 
tests/test_infrastructure.py
Location hierarchy, tree API, template creation, position capacity
[NEW] 
tests/test_assets.py
Asset CRUD, installation, movement, specifications, relationships
[NEW] 
tests/test_incidents.py
Incident lifecycle, assignment, timeline, work orders
[NEW] 
tests/test_maintenance.py
Checklists, schedules, history, due date calculation
[NEW] 
tests/test_stock.py
Stock transactions, ledger, current stock
[NEW] 
tests/test_reports.py
Report generation, export
[NEW] 
tests/test_permissions.py
RBAC enforcement across all protected endpoints
Phase 14 — Documentation & Scripts
[NEW] 
backend/README.md
Project overview, setup instructions, architecture, API summary
[NEW] 
scripts/create_superuser.py
CLI script to create admin user
[NEW] 
scripts/seed_permissions.py
Sync permission codes from a manifest to the database
Verification Plan
Automated Tests
bash

# Run all tests
pytest tests/ -v --tb=short
# Run with coverage
pytest tests/ --cov=app --cov-report=html
# Run specific module tests
pytest tests/test_auth.py -v
pytest tests/test_assets.py -v
Manual Verification
Application starts: uvicorn main:app --reload → no errors
OpenAPI docs: Visit /docs — all endpoints visible with schemas
Auth flow: Login → get tokens → access protected endpoint → refresh → logout
RBAC: Admin can CRUD users; Technician cannot
Asset lifecycle: Create asset → install → move → maintenance → incident → work order
Template creation: Create location from template → verify positions auto-created
Dashboard: Verify KPI aggregation matches seed data
Export: Export asset register as CSV/Excel → verify file content
Pagination: All list endpoints return proper paginated responses
Error handling: Invalid requests return consistent ApiResponse error format
Estimated File Count
Layer	Files
Core/Config	~8
Database	~3
ORM Models	~6
Schemas	~10
Repositories	~7
Services	~14
Dependencies/Middleware	~6
API Routers	~14
Workers	~5
Utils	~3
Tests	~12
Config/Scripts/Docs	~8
Total	~96 files
