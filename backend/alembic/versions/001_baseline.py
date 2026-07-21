"""Baseline migration for SIRMS v1.0 database schema.

Revision ID: 001_baseline
Revises: 
Create Date: 2026-01-01 00:00:00.000000

This is a baseline migration for the frozen database schema.
All DDL has already been applied via raw SQL scripts.
This migration simply stamps the baseline to track future migrations.
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Baseline - no operations needed as schema already exists
    pass


def downgrade() -> None:
    # Downgrade not supported for baseline
    pass
