"""Work Management Engine - Database Additions

Revision ID: 008_work_management_engine
Revises: 007_create_dispatch_module
"""

from alembic import op

revision = "008_work_management_engine"
down_revision = "007_create_dispatch_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create master.work_types ───────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS master.work_types (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            code        VARCHAR(50)  NOT NULL UNIQUE,
            description VARCHAR(255),
            is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP
        );
    """)

    # Seed work types
    op.execute("""
        INSERT INTO master.work_types (code, description)
        VALUES 
            ('INCIDENT', 'Standard Incident'),
            ('BREAKDOWN_MAINTENANCE', 'Breakdown Maintenance'),
            ('PREVENTIVE_MAINTENANCE', 'Preventive Maintenance'),
            ('CORRECTIVE_MAINTENANCE', 'Corrective Maintenance'),
            ('INSPECTION', 'Inspection'),
            ('INSTALLATION', 'Installation'),
            ('RELOCATION', 'Relocation'),
            ('DISPATCH', 'Dispatch'),
            ('VENDOR_REPAIR', 'Vendor Repair'),
            ('CALIBRATION', 'Calibration'),
            ('GENERAL_TASK', 'General Task'),
            ('WARRANTY', 'Warranty Claim'),
            ('UPGRADE', 'Asset Upgrade'),
            ('DECOMMISSION', 'Decommissioning')
        ON CONFLICT (code) DO NOTHING;
    """)

    # ── 2. Add work_type_id to incident.incidents ─────────────────────────────
    op.execute("""
        ALTER TABLE incident.incidents
        ADD COLUMN IF NOT EXISTS work_type_id UUID REFERENCES master.work_types(id);
    """)

    # Backfill existing incidents
    op.execute("""
        UPDATE incident.incidents
        SET work_type_id = (SELECT id FROM master.work_types WHERE code = 'INCIDENT')
        WHERE work_type_id IS NULL;
    """)

    # Enforce NOT NULL
    op.execute("""
        ALTER TABLE incident.incidents
        ALTER COLUMN work_type_id SET NOT NULL;
    """)

    # ── 3. Create incident.work_assignments ───────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.work_assignments (
            id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id         UUID         NOT NULL REFERENCES incident.incidents(id) ON DELETE CASCADE,
            assignment_type     VARCHAR(50)  NOT NULL,
            assigned_to         UUID         NOT NULL REFERENCES security.users(id),
            assigned_by         UUID         REFERENCES security.users(id),
            assigned_date       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            accepted_date       TIMESTAMP,
            started_date        TIMESTAMP,
            completed_date      TIMESTAMP,
            cancelled_date      TIMESTAMP,
            assignment_status   VARCHAR(50)  NOT NULL,
            remarks             TEXT
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_work_assignments_incident_id ON incident.work_assignments(incident_id);")

    # ── 4. Create incident.work_actions ───────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.work_actions (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id     UUID         NOT NULL REFERENCES incident.incidents(id) ON DELETE CASCADE,
            asset_id        UUID         REFERENCES asset.assets(id),
            action_type     VARCHAR(100) NOT NULL,
            user_id         UUID         NOT NULL REFERENCES security.users(id),
            timestamp       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reference_type  VARCHAR(100),
            reference_id    UUID
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_work_actions_incident_id ON incident.work_actions(incident_id);")

    # ── 5. Create incident.work_relations ─────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.work_relations (
            id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_incident_id  UUID         NOT NULL REFERENCES incident.incidents(id) ON DELETE CASCADE,
            target_incident_id  UUID         NOT NULL REFERENCES incident.incidents(id) ON DELETE CASCADE,
            relation_type       VARCHAR(50)  NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_work_relations_source_id ON incident.work_relations(source_incident_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_work_relations_target_id ON incident.work_relations(target_incident_id);")

    # ── 6. Recreate vw_incident_summary ───────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE VIEW incident.vw_incident_summary AS
        SELECT
            i.id AS incident_id,
            i.project_id,
            p.project_code,
            i.incident_number,
            wt.code AS work_type_code,
            wt.description AS work_type_description,
            ic.name AS incident_category_name,
            i.reported_date,
            i.asset_id,
            a.asset_number,
            i.location_id,
            l.code AS location_code,
            l.name AS location_name,
            ip.name AS priority_name,
            ist.name AS status_name,
            i.closed_date,
            i.description
        FROM incident.incidents i
        JOIN common.projects p ON p.id = i.project_id
        JOIN master.work_types wt ON wt.id = i.work_type_id
        LEFT JOIN master.incident_categories ic ON ic.id = i.incident_category_id
        LEFT JOIN asset.assets a ON a.id = i.asset_id
        LEFT JOIN infrastructure.locations l ON l.id = i.location_id
        JOIN master.incident_priority ip ON ip.id = i.incident_priority_id
        JOIN master.incident_status ist ON ist.id = i.incident_status_id;
    """)


def downgrade() -> None:
    raise NotImplementedError("Work Management Engine upgrade cannot be automatically downgraded.")
