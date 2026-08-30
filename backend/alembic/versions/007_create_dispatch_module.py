"""Create inventory schema with dispatch tables and DISPATCHED asset status.

Revision ID: 007_create_dispatch_module
Revises: 006_simplify_incident_management
"""

from alembic import op

revision = "007_create_dispatch_module"
down_revision = "006_simplify_incident_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Schema ────────────────────────────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS inventory")

    # ── Seed new DISPATCHED asset status ─────────────────────────────────────
    op.execute("""
        INSERT INTO master.asset_status (code, name, description, display_order)
        VALUES ('DISPATCHED', 'Dispatched', 'Asset has been dispatched to vendor/service centre', 90)
        ON CONFLICT (code) DO NOTHING
    """)

    # Also seed FAULTY / BEYOND_REPAIR if not present (used by receive logic)
    op.execute("""
        INSERT INTO master.asset_status (code, name, description, display_order)
        VALUES
            ('FAULTY',       'Faulty',        'Asset is faulty and requires repair',              80),
            ('BEYOND_REPAIR','Beyond Repair',  'Asset is beyond economical repair / condemned',    85)
        ON CONFLICT (code) DO NOTHING
    """)

    # ── number_sequences rows ─────────────────────────────────────────────────
    op.execute("""
        INSERT INTO common.number_sequences
            (entity_name, prefix, current_value, number_length, reset_policy)
        VALUES
            ('DISPATCH',         'DIS', 0, 5, 'FINANCIAL_YEAR'),
            ('DELIVERY_CHALLAN', 'DC',  0, 5, 'FINANCIAL_YEAR')
        ON CONFLICT (entity_name) DO NOTHING
    """)

    # ── dispatches ────────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS inventory.dispatches (
            id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            dispatch_no         VARCHAR(30)  NOT NULL UNIQUE,
            delivery_challan_no VARCHAR(30),
            dispatch_date       DATE         NOT NULL,
            vendor_id           UUID         REFERENCES common.vendors(id) ON DELETE RESTRICT,
            purpose             VARCHAR(30)  NOT NULL,
            courier_name        VARCHAR(150),
            tracking_number     VARCHAR(100),
            remarks             TEXT,
            status              VARCHAR(30)  NOT NULL DEFAULT 'DRAFT',
            created_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by          UUID         REFERENCES security.users(id) ON DELETE SET NULL,
            updated_at          TIMESTAMP,
            updated_by          UUID         REFERENCES security.users(id) ON DELETE SET NULL,
            is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
            CONSTRAINT chk_dispatches_purpose CHECK (
                purpose IN ('Repair', 'Warranty', 'Calibration', 'Transfer', 'Others')
            ),
            CONSTRAINT chk_dispatches_status CHECK (
                status IN ('Draft', 'Dispatched', 'Partially Returned', 'Closed', 'Cancelled')
            )
        )
    """)

    # ── dispatch_items ────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS inventory.dispatch_items (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            dispatch_id     UUID        NOT NULL REFERENCES inventory.dispatches(id) ON DELETE CASCADE,
            asset_id        UUID        REFERENCES asset.assets(id) ON DELETE RESTRICT,
            dispatch_type   VARCHAR(20) NOT NULL DEFAULT 'Asset',
            component_name  VARCHAR(200),
            quantity        INTEGER     NOT NULL DEFAULT 1,
            condition       VARCHAR(20) NOT NULL,
            status          VARCHAR(20) NOT NULL DEFAULT 'Out',
            return_date     DATE,
            result          VARCHAR(30),
            repair_cost     NUMERIC(14, 2),
            remarks         TEXT,
            created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by      UUID        REFERENCES security.users(id) ON DELETE SET NULL,
            updated_at      TIMESTAMP,
            updated_by      UUID        REFERENCES security.users(id) ON DELETE SET NULL,
            is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
            CONSTRAINT chk_dispatch_items_dispatch_type CHECK (
                dispatch_type IN ('Asset', 'Component')
            ),
            CONSTRAINT chk_dispatch_items_condition CHECK (
                condition IN ('Faulty', 'Working', 'Damaged')
            ),
            CONSTRAINT chk_dispatch_items_status CHECK (
                status IN ('Out', 'Returned')
            ),
            CONSTRAINT chk_dispatch_items_result CHECK (
                result IS NULL OR result IN ('Repaired', 'Replaced', 'Beyond Repair', 'Returned Without Repair')
            )
        )
    """)

    # ── Indexes ───────────────────────────────────────────────────────────────
    op.execute("CREATE INDEX IF NOT EXISTS idx_dispatches_status      ON inventory.dispatches(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dispatches_vendor_id   ON inventory.dispatches(vendor_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dispatches_dispatch_no ON inventory.dispatches(dispatch_no)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dispatch_items_dispatch ON inventory.dispatch_items(dispatch_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dispatch_items_asset    ON inventory.dispatch_items(asset_id)")


def downgrade() -> None:
    raise NotImplementedError(
        "Dispatch module downgrade is intentionally disabled. Drop tables manually if needed."
    )
