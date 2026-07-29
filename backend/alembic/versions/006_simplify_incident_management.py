"""Simplify incident management - Add resolution remarks and closed by, drop work orders."""

from alembic import op

revision = "006_simplify_incident_management"
down_revision = "005_refactor_position_infrastructure"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add closure fields and remove assigned_to from incidents
    op.execute("""
        ALTER TABLE incident.incidents
        ADD COLUMN IF NOT EXISTS resolution_remarks TEXT,
        ADD COLUMN IF NOT EXISTS closed_by UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL;
        
        ALTER TABLE incident.incidents
        DROP COLUMN IF EXISTS assigned_to;
    """)

    # 2. Drop work order related tables
    op.execute("""
        DROP TABLE IF EXISTS incident.work_order_tasks CASCADE;
        DROP TABLE IF EXISTS incident.work_orders CASCADE;
    """)


def downgrade() -> None:
    raise NotImplementedError("Simplifying incident management cannot be automatically downgraded.")
