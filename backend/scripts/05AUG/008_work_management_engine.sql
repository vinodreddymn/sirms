-- =============================================================================
-- File        : 008_work_management_engine.sql
-- Description : Work Management Engine - Database Additions
-- Revision    : 008_work_management_engine
-- Revises     : 007_create_dispatch_module
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. MASTER WORK TYPES
-- =============================================================================

CREATE TABLE IF NOT EXISTS master.work_types
(
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    code            VARCHAR(50) NOT NULL UNIQUE,

    description     VARCHAR(255),

    is_active       BOOLEAN NOT NULL DEFAULT TRUE,

    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at      TIMESTAMP
);

COMMENT ON TABLE master.work_types IS
'Master list of work types handled by the Work Management Engine.';


-- =============================================================================
-- Seed Work Types
-- =============================================================================

INSERT INTO master.work_types
(
    code,
    description
)
VALUES
    ('INCIDENT',                 'Standard Incident'),
    ('BREAKDOWN_MAINTENANCE',    'Breakdown Maintenance'),
    ('PREVENTIVE_MAINTENANCE',   'Preventive Maintenance'),
    ('CORRECTIVE_MAINTENANCE',   'Corrective Maintenance'),
    ('INSPECTION',               'Inspection'),
    ('INSTALLATION',             'Installation'),
    ('RELOCATION',               'Relocation'),
    ('DISPATCH',                 'Dispatch'),
    ('VENDOR_REPAIR',            'Vendor Repair'),
    ('CALIBRATION',              'Calibration'),
    ('GENERAL_TASK',             'General Task'),
    ('WARRANTY',                 'Warranty Claim'),
    ('UPGRADE',                  'Asset Upgrade'),
    ('DECOMMISSION',             'Decommissioning')
ON CONFLICT (code) DO NOTHING;


-- =============================================================================
-- 2. INCIDENTS TABLE
-- Add Work Type
-- =============================================================================

ALTER TABLE incident.incidents
ADD COLUMN IF NOT EXISTS work_type_id UUID;

ALTER TABLE incident.incidents
DROP CONSTRAINT IF EXISTS fk_incidents_work_type;

ALTER TABLE incident.incidents
ADD CONSTRAINT fk_incidents_work_type
FOREIGN KEY (work_type_id)
REFERENCES master.work_types(id);

-- -----------------------------------------------------------------------------
-- Backfill Existing Records
-- -----------------------------------------------------------------------------

UPDATE incident.incidents
SET work_type_id =
(
    SELECT id
    FROM master.work_types
    WHERE code = 'INCIDENT'
)
WHERE work_type_id IS NULL;

ALTER TABLE incident.incidents
ALTER COLUMN work_type_id SET NOT NULL;


-- =============================================================================
-- 3. WORK ASSIGNMENTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.work_assignments
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    incident_id             UUID NOT NULL,

    assignment_type         VARCHAR(50) NOT NULL,

    assigned_to             UUID NOT NULL,

    assigned_by             UUID,

    assigned_date           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    accepted_date           TIMESTAMP,

    started_date            TIMESTAMP,

    completed_date          TIMESTAMP,

    cancelled_date          TIMESTAMP,

    assignment_status       VARCHAR(50) NOT NULL,

    remarks                 TEXT,

    CONSTRAINT fk_work_assignment_incident
        FOREIGN KEY (incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_work_assignment_assigned_to
        FOREIGN KEY (assigned_to)
        REFERENCES security.users(id),

    CONSTRAINT fk_work_assignment_assigned_by
        FOREIGN KEY (assigned_by)
        REFERENCES security.users(id)
);

CREATE INDEX IF NOT EXISTS idx_work_assignments_incident_id
ON incident.work_assignments (incident_id);

COMMENT ON TABLE incident.work_assignments IS
'Stores assignment history for work orders.';


-- =============================================================================
-- 4. WORK ACTIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.work_actions
(
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    incident_id         UUID NOT NULL,

    asset_id            UUID,

    action_type         VARCHAR(100) NOT NULL,

    user_id             UUID NOT NULL,

    "timestamp"         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    reference_type      VARCHAR(100),

    reference_id        UUID,

    CONSTRAINT fk_work_action_incident
        FOREIGN KEY (incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_work_action_asset
        FOREIGN KEY (asset_id)
        REFERENCES asset.assets(id),

    CONSTRAINT fk_work_action_user
        FOREIGN KEY (user_id)
        REFERENCES security.users(id)
);

CREATE INDEX IF NOT EXISTS idx_work_actions_incident_id
ON incident.work_actions (incident_id);

COMMENT ON TABLE incident.work_actions IS
'Stores workflow audit trail and work actions.';


-- =============================================================================
-- 5. WORK RELATIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.work_relations
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_incident_id      UUID NOT NULL,

    target_incident_id      UUID NOT NULL,

    relation_type           VARCHAR(50) NOT NULL,

    CONSTRAINT fk_work_relation_source
        FOREIGN KEY (source_incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_work_relation_target
        FOREIGN KEY (target_incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_work_relations_source_id
ON incident.work_relations(source_incident_id);

CREATE INDEX IF NOT EXISTS idx_work_relations_target_id
ON incident.work_relations(target_incident_id);

COMMENT ON TABLE incident.work_relations IS
'Stores parent-child and related work order relationships.';


-- =============================================================================
-- 6. INCIDENT SUMMARY VIEW
-- =============================================================================

CREATE OR REPLACE VIEW incident.vw_incident_summary AS

SELECT

    i.id                             AS incident_id,

    i.project_id,

    p.project_code,

    i.incident_number,

    wt.code                          AS work_type_code,

    wt.description                   AS work_type_description,

    ic.name                          AS incident_category_name,

    i.reported_date,

    i.asset_id,

    a.asset_number,

    i.location_id,

    l.code                           AS location_code,

    l.name                           AS location_name,

    ip.name                          AS priority_name,

    ist.name                         AS status_name,

    i.closed_date,

    i.description

FROM incident.incidents i

INNER JOIN common.projects p
        ON p.id = i.project_id

INNER JOIN master.work_types wt
        ON wt.id = i.work_type_id

LEFT JOIN master.incident_categories ic
       ON ic.id = i.incident_category_id

LEFT JOIN asset.assets a
       ON a.id = i.asset_id

LEFT JOIN infrastructure.locations l
       ON l.id = i.location_id

INNER JOIN master.incident_priority ip
        ON ip.id = i.incident_priority_id

INNER JOIN master.incident_status ist
        ON ist.id = i.incident_status_id;


COMMENT ON VIEW incident.vw_incident_summary IS
'Summary view for all work orders and incidents.';

COMMIT;