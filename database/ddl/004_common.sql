/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Common
Description : Creates shared business and utility tables.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS common.customers
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_code           VARCHAR(30) NOT NULL UNIQUE,
    customer_name           VARCHAR(150) NOT NULL UNIQUE,
    contact_person          VARCHAR(120),
    contact_email           VARCHAR(150),
    contact_phone           VARCHAR(30),
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.projects
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id             UUID NOT NULL REFERENCES common.customers(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    project_type_id         BIGINT REFERENCES master.project_types(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    project_code            VARCHAR(30) NOT NULL UNIQUE,
    project_name            VARCHAR(150) NOT NULL UNIQUE,
    start_date              DATE,
    end_date                DATE,
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_projects_dates CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS common.vendors
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_code             VARCHAR(30) NOT NULL UNIQUE,
    vendor_name             VARCHAR(150) NOT NULL UNIQUE,
    vendor_type             VARCHAR(30) NOT NULL,
    contact_person          VARCHAR(120),
    contact_email           VARCHAR(150),
    contact_phone           VARCHAR(30),
    address_line            VARCHAR(255),
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_vendors_vendor_type CHECK (vendor_type IN ('OEM', 'REPAIR', 'AMC', 'INSTALLATION', 'SUPPLIER', 'OTHER'))
);

ALTER TABLE security.users
    ADD CONSTRAINT fk_users_default_project
    FOREIGN KEY (default_project_id) REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL;

ALTER TABLE security.user_roles
    ADD CONSTRAINT fk_user_roles_project
    FOREIGN KEY (project_id) REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS common.attachments
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    document_type_id        BIGINT REFERENCES master.document_types(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    file_name               VARCHAR(255) NOT NULL,
    file_path               VARCHAR(500) NOT NULL,
    mime_type               VARCHAR(100),
    file_size_bytes         BIGINT,
    checksum                VARCHAR(128),
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_attachments_file_size CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0)
);

CREATE TABLE IF NOT EXISTS common.audit_logs
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    user_id                 UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    schema_name             VARCHAR(50) NOT NULL,
    table_name              VARCHAR(150) NOT NULL,
    record_id               UUID,
    action_name             VARCHAR(30) NOT NULL,
    old_data                JSONB,
    new_data                JSONB,
    action_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address              VARCHAR(64),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.activity_logs
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    user_id                 UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    activity_type           VARCHAR(50) NOT NULL,
    module_name             VARCHAR(50) NOT NULL,
    entity_name             VARCHAR(50) NOT NULL,
    entity_id               UUID,
    activity_details        JSONB,
    activity_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.notifications
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    entity_name             VARCHAR(50),
    entity_id               UUID,
    notification_title      VARCHAR(150) NOT NULL,
    notification_body       TEXT NOT NULL,
    channel_type            VARCHAR(20) NOT NULL,
    sent_at                 TIMESTAMP,
    read_at                 TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_notifications_channel CHECK (channel_type IN ('EMAIL', 'SMS', 'PUSH', 'IN_APP'))
);

CREATE TABLE IF NOT EXISTS common.system_settings
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key             VARCHAR(100) NOT NULL UNIQUE,
    setting_value           TEXT NOT NULL,
    setting_group           VARCHAR(50) NOT NULL,
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.dashboard_preferences
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    preference_name         VARCHAR(100) NOT NULL,
    preference_json         JSONB NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_dashboard_preferences UNIQUE(user_id, project_id, preference_name)
);

CREATE TABLE IF NOT EXISTS common.saved_searches
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    search_name             VARCHAR(100) NOT NULL,
    module_name             VARCHAR(50) NOT NULL,
    search_criteria         JSONB NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.saved_filters
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    filter_name             VARCHAR(100) NOT NULL,
    module_name             VARCHAR(50) NOT NULL,
    filter_criteria         JSONB NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.report_definitions
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_code             VARCHAR(50) NOT NULL UNIQUE,
    report_name             VARCHAR(150) NOT NULL,
    module_name             VARCHAR(50) NOT NULL,
    definition_json         JSONB NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.saved_reports
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    report_definition_id    UUID NOT NULL REFERENCES common.report_definitions(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    report_name             VARCHAR(150) NOT NULL,
    parameters_json         JSONB,
    last_run_at             TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.qr_generation_history
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                UUID,
    generated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_by            UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    qr_value                VARCHAR(150) NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.qr_print_history
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                UUID,
    printed_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    printed_by              UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    copies_printed          INTEGER NOT NULL DEFAULT 1,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_qr_print_history_copies CHECK (copies_printed > 0)
);

CREATE TABLE IF NOT EXISTS common.barcode_history
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                UUID,
    barcode_value           VARCHAR(150) NOT NULL,
    generated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_by            UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.import_jobs
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    requested_by            UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    import_type             VARCHAR(50) NOT NULL,
    source_file_name        VARCHAR(255) NOT NULL,
    job_status              VARCHAR(20) NOT NULL,
    started_at              TIMESTAMP,
    finished_at             TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_import_jobs_status CHECK (job_status IN ('QUEUED', 'RUNNING', 'SUCCESS', 'FAILED'))
);

CREATE TABLE IF NOT EXISTS common.import_errors
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    import_job_id           UUID NOT NULL REFERENCES common.import_jobs(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    row_number              INTEGER,
    field_name              VARCHAR(100),
    error_message           TEXT NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.export_history
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    requested_by            UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    export_type             VARCHAR(50) NOT NULL,
    file_name               VARCHAR(255),
    exported_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.comments
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    entity_name             VARCHAR(50) NOT NULL,
    entity_id               UUID NOT NULL,
    commented_by            UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    comment_text            TEXT NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.tags
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_code                VARCHAR(50) NOT NULL UNIQUE,
    tag_name                VARCHAR(100) NOT NULL UNIQUE,
    tag_color               VARCHAR(20),
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS common.entity_tags
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_id                  UUID NOT NULL REFERENCES common.tags(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    entity_name             VARCHAR(50) NOT NULL,
    entity_id               UUID NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_entity_tags UNIQUE(tag_id, entity_name, entity_id)
);

CREATE TABLE IF NOT EXISTS common.favorite_assets
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    asset_id                UUID,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_favorite_assets UNIQUE(user_id, asset_id)
);

CREATE TABLE IF NOT EXISTS common.watch_list
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    incident_id             UUID,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_watch_list UNIQUE(user_id, incident_id)
);

CREATE TABLE IF NOT EXISTS common.notification_preferences
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    email_enabled           BOOLEAN NOT NULL DEFAULT TRUE,
    sms_enabled             BOOLEAN NOT NULL DEFAULT FALSE,
    push_enabled            BOOLEAN NOT NULL DEFAULT TRUE,
    quiet_hours_from        TIME,
    quiet_hours_to          TIME,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_notification_preferences UNIQUE(user_id)
);

CREATE TABLE IF NOT EXISTS common.number_sequences
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name             VARCHAR(50) NOT NULL UNIQUE,
    prefix                  VARCHAR(20) NOT NULL,
    current_value           BIGINT NOT NULL DEFAULT 0,
    number_length           INTEGER NOT NULL DEFAULT 6,
    reset_policy            VARCHAR(20) NOT NULL DEFAULT 'NEVER',
    last_reset_on           DATE,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_number_sequences_length CHECK (number_length BETWEEN 3 AND 12),
    CONSTRAINT chk_number_sequences_reset_policy CHECK (reset_policy IN ('NEVER', 'YEARLY', 'MONTHLY'))
);

COMMENT ON TABLE common.customers IS 'Customers or clients.';
COMMENT ON TABLE common.projects IS 'Projects belonging to customers.';
COMMENT ON TABLE common.vendors IS 'Suppliers, OEMs, repair vendors, and service vendors.';
COMMENT ON TABLE common.attachments IS 'Central attachment metadata repository.';
COMMENT ON TABLE common.audit_logs IS 'Low-level audit trail store.';
COMMENT ON TABLE common.activity_logs IS 'Business activity log store.';
COMMENT ON TABLE common.notifications IS 'Notification message history.';
COMMENT ON TABLE common.system_settings IS 'Application configuration store.';
COMMENT ON TABLE common.dashboard_preferences IS 'Per-user dashboard configuration.';
COMMENT ON TABLE common.saved_searches IS 'Saved search criteria.';
COMMENT ON TABLE common.saved_filters IS 'Saved filter criteria.';
COMMENT ON TABLE common.report_definitions IS 'Report definitions.';
COMMENT ON TABLE common.saved_reports IS 'User-saved report instances.';
COMMENT ON TABLE common.qr_generation_history IS 'QR code generation history.';
COMMENT ON TABLE common.qr_print_history IS 'QR code print history.';
COMMENT ON TABLE common.barcode_history IS 'Barcode generation history.';
COMMENT ON TABLE common.import_jobs IS 'Bulk import job store.';
COMMENT ON TABLE common.import_errors IS 'Import error details.';
COMMENT ON TABLE common.export_history IS 'Export operation history.';
COMMENT ON TABLE common.comments IS 'Generic comments store.';
COMMENT ON TABLE common.tags IS 'Reusable tag catalog.';
COMMENT ON TABLE common.entity_tags IS 'Tag assignments to arbitrary entities.';
COMMENT ON TABLE common.favorite_assets IS 'User favorite asset bookmarks.';
COMMENT ON TABLE common.watch_list IS 'Incident watch list records.';
COMMENT ON TABLE common.notification_preferences IS 'Per-user notification preferences.';
COMMENT ON TABLE common.number_sequences IS 'Configurable running number sequences by entity.';
