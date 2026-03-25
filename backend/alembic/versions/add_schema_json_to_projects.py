"""Add schema_json column to projects table

Revision ID: add_schema_json_to_projects
Revises: fix_all_schema_discrepancies
Create Date: 2026-03-24 17:03:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_schema_json_to_projects'
down_revision = 'fix_all_schema_discrepancies'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add schema_json column to projects table."""
    # Check if column exists before adding it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]
    
    # Add missing schema_json column to projects table
    if 'schema_json' not in columns:
        op.add_column('projects', sa.Column('schema_json', sa.JSON(), nullable=True))

def downgrade() -> None:
    """Remove schema_json column from projects table."""
    # Drop the column if it exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]
    
    if 'schema_json' in columns:
        op.drop_column('projects', 'schema_json')