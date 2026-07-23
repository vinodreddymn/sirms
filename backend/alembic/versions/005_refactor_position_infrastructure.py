"""Refactor installation model - Move fixed infrastructure to Position (location_positions)."""

from alembic import op

revision = "005_refactor_position_infrastructure"
down_revision = "004_add_asset_applicability_mappings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add fixed infrastructure fields to infrastructure.location_positions
    op.execute("""
        ALTER TABLE infrastructure.location_positions
        ADD COLUMN IF NOT EXISTS power_source VARCHAR(100),
        ADD COLUMN IF NOT EXISTS electrical_panel VARCHAR(100),
        ADD COLUMN IF NOT EXISTS network_switch VARCHAR(100),
        ADD COLUMN IF NOT EXISTS switch_port VARCHAR(50),
        ADD COLUMN IF NOT EXISTS patch_panel VARCHAR(100),
        ADD COLUMN IF NOT EXISTS junction_box VARCHAR(100),
        ADD COLUMN IF NOT EXISTS mounting_details TEXT,
        ADD COLUMN IF NOT EXISTS infrastructure_details JSONB;
    """)

    # 2. Ensure event-specific fields on asset.asset_installations
    op.execute("""
        ALTER TABLE asset.asset_installations
        ADD COLUMN IF NOT EXISTS installation_status VARCHAR(30) DEFAULT 'INSTALLED',
        ADD COLUMN IF NOT EXISTS installed_by UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
        ADD COLUMN IF NOT EXISTS removed_by UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
        ADD COLUMN IF NOT EXISTS remarks TEXT;
    """)


def downgrade() -> None:
    raise NotImplementedError("Structural infrastructure refactoring cannot be automatically downgraded.")
