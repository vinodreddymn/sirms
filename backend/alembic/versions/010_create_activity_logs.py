"""Create activity logs table in common schema

Revision ID: 010_create_activity_logs
Revises: 009_work_management_detail_tables
"""

from alembic import op

revision = "010_create_activity_logs"
down_revision = "009_work_management_detail_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure the activity_logs table exists with the columns our SQLAlchemy model expects.
    # If the table already exists (older schema), add any missing columns so code and DB stay in sync.
    op.execute("""
    CREATE TABLE IF NOT EXISTS common.activity_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_id UUID REFERENCES common.projects(id),
        user_id UUID REFERENCES security.users(id),
        activity_type VARCHAR(50) NOT NULL DEFAULT '',
        module_name VARCHAR(50) NOT NULL DEFAULT '',
        entity_name VARCHAR(50) NOT NULL DEFAULT '',
        entity_id UUID,
        activity_details JSONB NOT NULL DEFAULT '{}'::jsonb,
        activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        created_by UUID REFERENCES security.users(id),
        updated_at TIMESTAMP,
        updated_by UUID REFERENCES security.users(id),
        is_active BOOLEAN NOT NULL DEFAULT TRUE
    );
    """)

    # Add any missing columns to an existing table (safe to run repeatedly)
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS project_id UUID REFERENCES common.projects(id);")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES security.users(id);")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS activity_type VARCHAR(50) NOT NULL DEFAULT '';")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS module_name VARCHAR(50) NOT NULL DEFAULT '';")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS entity_name VARCHAR(50) NOT NULL DEFAULT '';")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS entity_id UUID;")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS activity_details JSONB NOT NULL DEFAULT '{}'::jsonb;")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;")
    op.execute("ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;")

    # Create useful indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_activity_logs_time ON common.activity_logs(activity_at DESC);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_activity_logs_module ON common.activity_logs(module_name);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_activity_logs_type ON common.activity_logs(activity_type);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_activity_logs_created_by ON common.activity_logs(created_by);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_activity_logs_project ON common.activity_logs(project_id);")
        # Backfill from older column names if present (safe, idempotent)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema='common' AND table_name='activity_logs' AND column_name='module') THEN
                ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS module_name VARCHAR(50) NOT NULL DEFAULT '';
                UPDATE common.activity_logs SET module_name = module WHERE (module_name IS NULL OR module_name = '') AND (module IS NOT NULL);
            END IF;

            IF EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema='common' AND table_name='activity_logs' AND column_name='action') THEN
                ALTER TABLE common.activity_logs ADD COLUMN IF NOT EXISTS activity_type VARCHAR(50) NOT NULL DEFAULT '';
                UPDATE common.activity_logs SET activity_type = action WHERE (activity_type IS NULL OR activity_type = '') AND (action IS NOT NULL);
            END IF;
        END$$;
        """)


def downgrade() -> None:
    raise NotImplementedError("Activity logs are append-only and should not be downgraded automatically.")
