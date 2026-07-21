"""Add manufacturer and vendor asset applicability mappings."""

from alembic import op

revision = "004_add_asset_applicability_mappings"
down_revision = "003_add_om_asset_operations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS master.manufacturer_asset_scopes (
          id BIGSERIAL PRIMARY KEY, manufacturer_id BIGINT NOT NULL REFERENCES master.manufacturers(id) ON DELETE CASCADE,
          asset_category_id BIGINT NOT NULL REFERENCES master.asset_categories(id) ON DELETE RESTRICT,
          asset_subcategory_id BIGINT REFERENCES master.asset_subcategories(id) ON DELETE RESTRICT,
          is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT uq_manufacturer_asset_scope UNIQUE(manufacturer_id, asset_category_id, asset_subcategory_id)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS common.vendor_asset_scopes (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(), vendor_id UUID NOT NULL REFERENCES common.vendors(id) ON DELETE CASCADE,
          asset_category_id BIGINT NOT NULL REFERENCES master.asset_categories(id) ON DELETE RESTRICT,
          asset_subcategory_id BIGINT REFERENCES master.asset_subcategories(id) ON DELETE RESTRICT,
          manufacturer_id BIGINT REFERENCES master.manufacturers(id) ON DELETE RESTRICT,
          service_type VARCHAR(30), is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT uq_vendor_asset_scope UNIQUE(vendor_id, asset_category_id, asset_subcategory_id, manufacturer_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_manufacturer_asset_scopes_filter ON master.manufacturer_asset_scopes(asset_category_id, asset_subcategory_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_vendor_asset_scopes_filter ON common.vendor_asset_scopes(asset_category_id, asset_subcategory_id, manufacturer_id)")


def downgrade() -> None:
    raise NotImplementedError("Applicability mappings are operational configuration and must not be removed automatically.")
