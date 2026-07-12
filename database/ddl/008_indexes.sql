/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Indexes
Description : Creates join, search, and lifecycle indexes.
===============================================================================
*/

CREATE INDEX IF NOT EXISTS idx_location_template_nodes_template ON master.location_template_nodes(location_template_id);
CREATE INDEX IF NOT EXISTS idx_location_template_nodes_parent ON master.location_template_nodes(parent_node_id);
CREATE INDEX IF NOT EXISTS idx_position_template_nodes_template ON master.position_template_nodes(position_template_id);
CREATE INDEX IF NOT EXISTS idx_asset_subcategories_category_id ON master.asset_subcategories(asset_category_id);
CREATE INDEX IF NOT EXISTS idx_asset_models_manufacturer_id ON master.asset_models(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_asset_models_asset_subcategory_id ON master.asset_models(asset_subcategory_id);
CREATE INDEX IF NOT EXISTS idx_specification_definitions_category ON master.specification_definitions(asset_category_id);
CREATE INDEX IF NOT EXISTS idx_specification_definitions_subcategory ON master.specification_definitions(asset_subcategory_id);

CREATE INDEX IF NOT EXISTS idx_projects_customer_id ON common.projects(customer_id);
CREATE INDEX IF NOT EXISTS idx_users_default_project_id ON security.users(default_project_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON security.role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON security.role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_security_user_roles_user_id ON security.user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_security_user_roles_role_id ON security.user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_security_user_roles_project_id ON security.user_roles(project_id);
CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON security.login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON security.password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON security.refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_api_tokens_user_id ON security.api_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_locations_project_id ON infrastructure.locations(project_id);
CREATE INDEX IF NOT EXISTS idx_locations_parent_location_id ON infrastructure.locations(parent_location_id);
CREATE INDEX IF NOT EXISTS idx_locations_location_type_id ON infrastructure.locations(location_type_id);
CREATE INDEX IF NOT EXISTS idx_locations_name ON infrastructure.locations(name);
CREATE INDEX IF NOT EXISTS idx_location_positions_location_id ON infrastructure.location_positions(location_id);
CREATE INDEX IF NOT EXISTS idx_location_positions_position_type_id ON infrastructure.location_positions(position_type_id);

CREATE INDEX IF NOT EXISTS idx_assets_project_id ON asset.assets(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_asset_category_id ON asset.assets(asset_category_id);
CREATE INDEX IF NOT EXISTS idx_assets_asset_subcategory_id ON asset.assets(asset_subcategory_id);
CREATE INDEX IF NOT EXISTS idx_assets_asset_status_id ON asset.assets(asset_status_id);
CREATE INDEX IF NOT EXISTS idx_assets_asset_lifecycle_id ON asset.assets(asset_lifecycle_id);
CREATE INDEX IF NOT EXISTS idx_assets_current_location_id ON asset.assets(current_location_id);
CREATE INDEX IF NOT EXISTS idx_assets_asset_number ON asset.assets(asset_number);
CREATE INDEX IF NOT EXISTS idx_asset_specifications_asset_id ON asset.asset_specifications(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_installations_asset_id ON asset.asset_installations(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_installations_location_position_id ON asset.asset_installations(location_position_id);
CREATE INDEX IF NOT EXISTS idx_asset_installations_current_flag ON asset.asset_installations(current_flag);
CREATE INDEX IF NOT EXISTS idx_asset_movements_asset_id ON asset.asset_movements(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_movements_movement_date ON asset.asset_movements(movement_date);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_project_id ON asset.stock_transactions(project_id);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_asset_id ON asset.stock_transactions(asset_id);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_location_id ON asset.stock_transactions(location_id);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_transaction_date ON asset.stock_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_asset_documents_asset_id ON asset.asset_documents(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_photos_asset_id ON asset.asset_photos(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_relationships_asset_id ON asset.asset_relationships(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_relationships_related_asset_id ON asset.asset_relationships(related_asset_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_asset_id ON asset.maintenance_schedules(asset_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_next_due_date ON asset.maintenance_schedules(next_due_date);
CREATE INDEX IF NOT EXISTS idx_maintenance_history_asset_id ON asset.maintenance_history(asset_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_history_performed_on ON asset.maintenance_history(performed_on);

CREATE INDEX IF NOT EXISTS idx_incidents_project_id ON incident.incidents(project_id);
CREATE INDEX IF NOT EXISTS idx_incidents_asset_id ON incident.incidents(asset_id);
CREATE INDEX IF NOT EXISTS idx_incidents_location_id ON incident.incidents(location_id);
CREATE INDEX IF NOT EXISTS idx_incidents_incident_status_id ON incident.incidents(incident_status_id);
CREATE INDEX IF NOT EXISTS idx_incidents_incident_number ON incident.incidents(incident_number);
CREATE INDEX IF NOT EXISTS idx_incident_updates_incident_id ON incident.incident_updates(incident_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_incident_id ON incident.work_orders(incident_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_work_order_number ON incident.work_orders(work_order_number);
CREATE INDEX IF NOT EXISTS idx_work_order_tasks_work_order_id ON incident.work_order_tasks(work_order_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_action_at ON common.audit_logs(action_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_record ON common.audit_logs(schema_name, table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON common.activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON common.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON common.saved_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_filters_user_id ON common.saved_filters(user_id);
CREATE INDEX IF NOT EXISTS idx_import_errors_import_job_id ON common.import_errors(import_job_id);
CREATE INDEX IF NOT EXISTS idx_comments_entity ON common.comments(entity_name, entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_tags_entity ON common.entity_tags(entity_name, entity_id);
