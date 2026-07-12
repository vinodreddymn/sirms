/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Incident
Description : Creates incidents, updates, work orders, and attachment tables.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS incident.incidents
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id                  UUID NOT NULL REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    incident_number             VARCHAR(50) NOT NULL UNIQUE,
    incident_category_id        BIGINT REFERENCES master.incident_categories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    reported_date               TIMESTAMP NOT NULL,
    asset_id                    UUID REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    location_id                 UUID REFERENCES infrastructure.locations(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    reported_by                 UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    incident_priority_id        BIGINT NOT NULL REFERENCES master.incident_priority(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    description                 TEXT NOT NULL,
    incident_status_id          BIGINT NOT NULL REFERENCES master.incident_status(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    assigned_to                 UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    closed_date                 TIMESTAMP,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_incidents_closed_date CHECK (closed_date IS NULL OR closed_date >= reported_date)
);

CREATE TABLE IF NOT EXISTS incident.incident_updates
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id                 UUID NOT NULL REFERENCES incident.incidents(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    update_datetime             TIMESTAMP NOT NULL,
    update_user_id              UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    remarks                     TEXT NOT NULL,
    status_after_update_id      BIGINT REFERENCES master.incident_status(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID
);

CREATE TABLE IF NOT EXISTS incident.work_orders
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_order_number           VARCHAR(50) NOT NULL UNIQUE,
    incident_id                 UUID NOT NULL REFERENCES incident.incidents(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    assigned_to                 UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    vendor_id                   UUID REFERENCES common.vendors(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    planned_start               TIMESTAMP,
    actual_start                TIMESTAMP,
    actual_finish               TIMESTAMP,
    work_order_status_id        BIGINT NOT NULL REFERENCES master.work_order_status(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    completion_notes            TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_work_orders_timing CHECK (actual_finish IS NULL OR actual_start IS NULL OR actual_finish >= actual_start)
);

CREATE TABLE IF NOT EXISTS incident.work_order_tasks
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_order_id               UUID NOT NULL REFERENCES incident.work_orders(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    task_sequence               INTEGER NOT NULL,
    task_description            VARCHAR(255) NOT NULL,
    assigned_to                 UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    completed_on                TIMESTAMP,
    completion_notes            TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_work_order_tasks UNIQUE(work_order_id, task_sequence),
    CONSTRAINT chk_work_order_tasks_sequence CHECK (task_sequence > 0)
);

CREATE TABLE IF NOT EXISTS incident.incident_attachments
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id                 UUID NOT NULL REFERENCES incident.incidents(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    attachment_id               UUID NOT NULL REFERENCES common.attachments(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    attachment_category         VARCHAR(20) NOT NULL,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_incident_attachment_category CHECK (attachment_category IN ('PHOTO', 'VIDEO', 'DOCUMENT'))
);

ALTER TABLE common.watch_list
    ADD CONSTRAINT fk_watch_list_incident
    FOREIGN KEY (incident_id) REFERENCES incident.incidents(id) ON UPDATE RESTRICT ON DELETE CASCADE;

COMMENT ON TABLE incident.incidents IS 'Incident register.';
COMMENT ON TABLE incident.incident_updates IS 'Timeline updates for incidents.';
COMMENT ON TABLE incident.work_orders IS 'Work orders generated from incidents.';
COMMENT ON TABLE incident.work_order_tasks IS 'Detailed tasks under work orders.';
COMMENT ON TABLE incident.incident_attachments IS 'Attachments linked to incidents.';
