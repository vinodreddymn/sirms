"""Generalize Work Requests

Revision ID: 009_generalize_work_requests
Revises: 008_work_management_engine
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "009_generalize_work_requests"
down_revision = "008_work_management_engine"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Drop existing view to prevent dependency errors during rename
    op.execute("DROP VIEW IF EXISTS incident.vw_incident_summary;")

    # 2. Rename columns in incident.incidents
    op.alter_column('incidents', 'incident_number', new_column_name='work_request_number', schema='incident')
    op.alter_column('incidents', 'incident_status_id', new_column_name='status_id', schema='incident')
    op.alter_column('incidents', 'incident_priority_id', new_column_name='priority_id', schema='incident')
    op.alter_column('incidents', 'incident_category_id', new_column_name='category_id', schema='incident')
    op.alter_column('incidents', 'resolution_remarks', new_column_name='completion_notes', schema='incident')

    # 3. Add SLA, assignment, and cost fields to incident.incidents
    op.add_column('incidents', sa.Column('assigned_to_id', UUID(as_uuid=True), sa.ForeignKey('security.users.id', ondelete='SET NULL', onupdate='RESTRICT'), nullable=True), schema='incident')
    op.add_column('incidents', sa.Column('target_start_date', sa.DateTime(), nullable=True), schema='incident')
    op.add_column('incidents', sa.Column('target_completion_date', sa.DateTime(), nullable=True), schema='incident')
    op.add_column('incidents', sa.Column('actual_start_date', sa.DateTime(), nullable=True), schema='incident')
    op.add_column('incidents', sa.Column('actual_completion_date', sa.DateTime(), nullable=True), schema='incident')
    op.add_column('incidents', sa.Column('estimated_cost', sa.Numeric(precision=12, scale=2), nullable=True), schema='incident')
    op.add_column('incidents', sa.Column('actual_cost', sa.Numeric(precision=12, scale=2), nullable=True), schema='incident')

    # 4. Add time_spent_minutes to incident_updates
    op.add_column('incident_updates', sa.Column('time_spent_minutes', sa.Integer(), nullable=True), schema='incident')

    # 5. Recreate View with new names as vw_work_request_summary
    op.execute("""
        CREATE OR REPLACE VIEW incident.vw_work_request_summary AS
        SELECT
            i.id AS incident_id,
            i.project_id,
            p.project_code,
            i.work_request_number AS incident_number,
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
        LEFT JOIN master.incident_categories ic ON ic.id = i.category_id
        LEFT JOIN asset.assets a ON a.id = i.asset_id
        LEFT JOIN infrastructure.locations l ON l.id = i.location_id
        JOIN master.incident_priority ip ON ip.id = i.priority_id
        JOIN master.incident_status ist ON ist.id = i.status_id;
    """)

def downgrade() -> None:
    raise NotImplementedError("Work Request Generalization upgrade cannot be automatically downgraded.")
