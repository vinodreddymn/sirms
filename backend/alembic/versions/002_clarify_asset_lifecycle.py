"""Clarify asset lifecycle stages.

Revision ID: 002_clarify_asset_lifecycle
Revises: 001_baseline
Create Date: 2026-07-15 00:00:00.000000
"""

from alembic import op


revision = "002_clarify_asset_lifecycle"
down_revision = "001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE master.asset_lifecycle
        SET code = 'DECOMMISSIONED',
            name = 'Decommissioned',
            description = 'Lifecycle stage: removed from service and awaiting retirement or disposal',
            display_order = 4
        WHERE code = 'REPAIR'
        """,
    )
    op.execute(
        """
        UPDATE master.asset_lifecycle
        SET description = CASE code
            WHEN 'PROCURED' THEN 'Lifecycle stage: acquired and awaiting commissioning'
            WHEN 'COMMISSIONED' THEN 'Lifecycle stage: accepted and commissioned for use'
            WHEN 'IN_SERVICE' THEN 'Lifecycle stage: part of the active asset portfolio'
            WHEN 'RETIRED' THEN 'Lifecycle stage: permanently removed from service'
            ELSE description
        END
        WHERE code IN ('PROCURED', 'COMMISSIONED', 'IN_SERVICE', 'RETIRED')
        """,
    )
    op.execute(
        """
        INSERT INTO master.asset_lifecycle (code, name, description, display_order)
        VALUES ('DISPOSED', 'Disposed', 'Lifecycle stage: formally disposed after retirement', 6)
        ON CONFLICT (code) DO UPDATE
        SET name = EXCLUDED.name,
            description = EXCLUDED.description,
            display_order = EXCLUDED.display_order
        """,
    )
    op.execute(
        """
        UPDATE master.asset_status
        SET description = CASE code
            WHEN 'IN_STOCK' THEN 'Current operating state: available in store'
            WHEN 'INSTALLED' THEN 'Current operating state: installed at a site'
            WHEN 'UNDER_REPAIR' THEN 'Current operating state: temporarily unavailable for repair'
            WHEN 'SCRAPPED' THEN 'Current operating state: disposed and unavailable'
            ELSE description
        END
        WHERE code IN ('IN_STOCK', 'INSTALLED', 'UNDER_REPAIR', 'SCRAPPED')
        """,
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE master.asset_lifecycle
        SET code = 'REPAIR',
            name = 'Repair',
            description = 'Under repair lifecycle stage',
            display_order = 4
        WHERE code = 'DECOMMISSIONED'
        """,
    )
    op.execute("DELETE FROM master.asset_lifecycle WHERE code = 'DISPOSED'")
