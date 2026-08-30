-- =============================================================================
-- Migration : 009_work_management_detail_tables.sql
-- Description: Create detail tables for Work Management Engine
-- Revises   : 008_work_management_engine
-- =============================================================================

BEGIN;

-- =============================================================================
-- Preventive Maintenance Details
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.pm_details
(
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    incident_id         UUID NOT NULL UNIQUE,

    scheduled_date      DATE,
    completion_date     DATE,

    pm_checklist_id     UUID,

    remarks             TEXT,

    CONSTRAINT fk_pm_details_incident
        FOREIGN KEY (incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE incident.pm_details IS
'Stores Preventive Maintenance specific information for PM work orders.';


-- =============================================================================
-- Inspection Details
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.inspection_details
(
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    incident_id         UUID NOT NULL UNIQUE,

    inspection_date     DATE,

    inspector_id        UUID,

    result              VARCHAR(50),

    remarks             TEXT,

    CONSTRAINT fk_inspection_incident
        FOREIGN KEY (incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_inspection_inspector
        FOREIGN KEY (inspector_id)
        REFERENCES security.users(id)
        ON DELETE SET NULL
);

COMMENT ON TABLE incident.inspection_details IS
'Stores inspection specific information.';


-- =============================================================================
-- Installation Details
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.installation_details
(
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    incident_id         UUID NOT NULL UNIQUE,

    installation_date   DATE,

    installed_by        UUID,

    sign_off_date       DATE,

    remarks             TEXT,

    CONSTRAINT fk_installation_incident
        FOREIGN KEY (incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_installation_user
        FOREIGN KEY (installed_by)
        REFERENCES security.users(id)
        ON DELETE SET NULL
);

COMMENT ON TABLE incident.installation_details IS
'Stores installation and commissioning details.';


-- =============================================================================
-- Vendor Repair Details
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.vendor_repair_details
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    incident_id             UUID NOT NULL UNIQUE,

    vendor_id               UUID,

    dispatch_date           DATE,

    expected_return_date    DATE,

    actual_return_date      DATE,

    repair_cost             NUMERIC(12,2),

    remarks                 TEXT,

    CONSTRAINT fk_vendorrepair_incident
        FOREIGN KEY (incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE incident.vendor_repair_details IS
'Stores vendor/OEM repair information.';


-- =============================================================================
-- Calibration Details
-- =============================================================================

CREATE TABLE IF NOT EXISTS incident.calibration_details
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    incident_id             UUID NOT NULL UNIQUE,

    calibration_date        DATE,

    next_due_date           DATE,

    calibrated_by           UUID,

    certificate_number      VARCHAR(100),

    result                  VARCHAR(50),

    remarks                 TEXT,

    CONSTRAINT fk_calibration_incident
        FOREIGN KEY (incident_id)
        REFERENCES incident.incidents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_calibration_user
        FOREIGN KEY (calibrated_by)
        REFERENCES security.users(id)
        ON DELETE SET NULL
);

COMMENT ON TABLE incident.calibration_details IS
'Stores calibration and certification information.';

COMMIT;