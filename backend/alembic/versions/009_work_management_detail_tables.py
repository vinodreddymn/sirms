"""Work Management Engine - Detail Tables

Revision ID: 009_work_management_detail_tables
Revises: 008_work_management_engine
"""

from alembic import op

revision = "009_work_management_detail_tables"
down_revision = "008_work_management_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create incident.pm_details ─────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.pm_details (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id     UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
            scheduled_date  DATE,
            completion_date DATE,
            pm_checklist_id UUID,
            remarks         TEXT
        );
    """)

    # ── 2. Create incident.inspection_details ─────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.inspection_details (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id     UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
            inspection_date DATE,
            inspector_id    UUID REFERENCES security.users(id) ON DELETE SET NULL,
            result          VARCHAR(50),
            remarks         TEXT
        );
    """)

    # ── 3. Create incident.installation_details ───────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.installation_details (
            id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id       UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
            installation_date DATE,
            installed_by      UUID REFERENCES security.users(id) ON DELETE SET NULL,
            sign_off_date     DATE,
            remarks           TEXT
        );
    """)

    # ── 4. Create incident.vendor_repair_details ──────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.vendor_repair_details (
            id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id          UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
            vendor_id            UUID,
            dispatch_date        DATE,
            expected_return_date DATE,
            actual_return_date   DATE,
            repair_cost          NUMERIC(12, 2),
            remarks              TEXT
        );
    """)

    # ── 5. Create incident.calibration_details ────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident.calibration_details (
            id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id        UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
            calibration_date   DATE,
            next_due_date      DATE,
            calibrated_by      UUID REFERENCES security.users(id) ON DELETE SET NULL,
            certificate_number VARCHAR(100),
            result             VARCHAR(50),
            remarks            TEXT
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS incident.calibration_details CASCADE;")
    op.execute("DROP TABLE IF EXISTS incident.vendor_repair_details CASCADE;")
    op.execute("DROP TABLE IF EXISTS incident.installation_details CASCADE;")
    op.execute("DROP TABLE IF EXISTS incident.inspection_details CASCADE;")
    op.execute("DROP TABLE IF EXISTS incident.pm_details CASCADE;")
