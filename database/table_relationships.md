# Table Relationship Guide

This file explains the purpose and principal relationships for every Version 1.0 table.

## `master` schema

- `master.location_types`: Location type lookup used by `infrastructure.locations`.
- `master.location_templates`: Header table for reusable location structures.
- `master.location_template_nodes`: Child nodes under a location template; references `master.location_types` and optional `master.position_templates`.
- `master.position_types`: Position type lookup used by positions and position templates.
- `master.position_templates`: Header table for reusable position sets.
- `master.position_template_nodes`: Child position nodes under a position template; references `master.position_types`.
- `master.asset_categories`: Top-level asset grouping.
- `master.asset_subcategories`: Child grouping under asset categories; used by assets, models, specs, and maintenance checklist targeting.
- `master.manufacturers`: Manufacturer catalog used by asset models and assets.
- `master.asset_models`: Model catalog tied to manufacturer and optional subcategory.
- `master.asset_status`: Current operational state lookup for assets.
- `master.asset_condition`: Physical condition lookup for assets.
- `master.asset_lifecycle`: Lifecycle stage lookup for assets.
- `master.maintenance_types`: Maintenance type lookup for schedules, history, and checklists.
- `master.failure_categories`: Failure classification lookup for maintenance history.
- `master.root_cause_categories`: Root cause classification lookup for maintenance history.
- `master.incident_status`: Incident lifecycle lookup used by incidents and incident updates.
- `master.incident_priority`: Incident urgency lookup.
- `master.incident_categories`: Incident classification lookup.
- `master.work_order_status`: Work order lifecycle lookup.
- `master.relationship_types`: Asset-to-asset relationship lookup.
- `master.document_types`: Document classification lookup used by attachments and asset documents.
- `master.photo_types`: Photo classification lookup used by asset photos.
- `master.project_types`: Project type lookup used by `common.projects`.
- `master.user_role_templates`: Role template lookup used by runtime security roles.
- `master.specification_definitions`: Configurable asset specification metadata used by `asset.asset_specifications`.
- `master.movement_types`: Asset movement classification lookup.
- `master.stock_transaction_types`: Stock ledger classification lookup with quantity effect.

## `security` schema

- `security.users`: Core application user table; referenced across incidents, maintenance, notifications, comments, and activity/audit logs.
- `security.roles`: Runtime roles that can optionally map back to `master.user_role_templates`.
- `security.permissions`: Permission catalog grouped by module.
- `security.role_permissions`: Bridge assigning permissions to roles.
- `security.user_roles`: Bridge assigning roles to users, optionally scoped to a project.
- `security.login_history`: Authentication event history for users.
- `security.password_reset_tokens`: Password reset token history for users.
- `security.refresh_tokens`: Session refresh token history for users.
- `security.api_tokens`: Future-ready API token store per user.

## `common` schema

- `common.customers`: Customer master; parent of `common.projects`.
- `common.projects`: Project master; parent or context holder for locations, assets, incidents, reports, and shared utilities.
- `common.vendors`: Vendor master used by asset movement, maintenance, and work orders.
- `common.attachments`: Central attachment metadata store used by asset and incident attachment tables.
- `common.audit_logs`: Low-level data-change audit records with optional project and user linkage.
- `common.activity_logs`: Business activity history with optional project and user linkage.
- `common.notifications`: Notification history by user and optional project or entity context.
- `common.system_settings`: Global application setting store.
- `common.dashboard_preferences`: Per-user dashboard preferences with optional project scope.
- `common.saved_searches`: Per-user reusable search definitions.
- `common.saved_filters`: Per-user reusable filter definitions.
- `common.report_definitions`: Report catalog used by saved reports.
- `common.saved_reports`: User-saved report references tied to a report definition.
- `common.qr_generation_history`: QR generation history tied to assets after asset migration.
- `common.qr_print_history`: QR print history tied to assets after asset migration.
- `common.barcode_history`: Barcode generation history tied to assets after asset migration.
- `common.import_jobs`: Bulk import jobs; parent of `common.import_errors`.
- `common.import_errors`: Row-level import error details.
- `common.export_history`: Export operation history.
- `common.comments`: Generic comments store keyed by `entity_name` and `entity_id`.
- `common.tags`: Tag catalog.
- `common.entity_tags`: Generic bridge linking tags to arbitrary entities.
- `common.favorite_assets`: User-to-asset bookmark bridge.
- `common.watch_list`: User-to-incident watch bridge.
- `common.notification_preferences`: Per-user notification channel preferences.
- `common.number_sequences`: Configurable numbering configuration used by helper functions and application workflows.

## `infrastructure` schema

- `infrastructure.locations`: Unlimited-depth hierarchical location register within a project, with optional source template node and GIS-ready attributes.
- `infrastructure.location_positions`: Installable positions under a location, with optional source position template node.

## `asset` schema

- `asset.assets`: Core asset register linked to project, category, subcategory, model, status, condition, lifecycle, and optional current location.
- `asset.asset_specifications`: Dynamic specification values for an asset; each row references a single definition from `master.specification_definitions`.
- `asset.asset_installations`: Historical installation records linking assets to physical location positions.
- `asset.asset_movements`: Permanent asset movement log across locations and vendors.
- `asset.stock_transactions`: Stock ledger records by project, asset, transaction type, location, and vendor.
- `asset.asset_documents`: Asset document metadata with optional binary metadata in `common.attachments`.
- `asset.asset_photos`: Asset photo metadata with optional binary metadata in `common.attachments`.
- `asset.asset_relationships`: Self-referencing bridge between related assets.
- `asset.maintenance_checklists`: Checklist headers for a maintenance type and optional asset subcategory.
- `asset.checklist_items`: Child line items under a maintenance checklist.
- `asset.maintenance_schedules`: Planned future maintenance for an asset, with optional technician and vendor assignment.
- `asset.maintenance_history`: Completed maintenance history for an asset, optionally tied to a schedule, checklist, vendor, and failure/root-cause analysis.

## `incident` schema

- `incident.incidents`: Core incident register linked to project and optionally an asset and/or location.
- `incident.incident_updates`: Append-only incident timeline entries, with `update_user_id` capturing the actor and audit columns retained separately.
- `incident.work_orders`: Work orders raised from incidents, optionally tied to a vendor and technician.
- `incident.work_order_tasks`: Child task lines under a work order.
- `incident.incident_attachments`: Attachment bridge between incidents and `common.attachments`.
