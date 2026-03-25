"""Add is_saved column to projects table

Revision ID: add_is_saved_to_projects
Revises: add_schema_json_to_projects
Create Date: 2026-03-24 17:13:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_is_saved_to_projects'
down_revision = 'add_schema_json_to_projects'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add is_saved column to projects table."""
    # Check if column exists before adding
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]
    
    if 'is_saved' not in columns:
        op.add_column('projects', sa.Column('is_saved', sa.Boolean(), nullable=False, server_default='false'))

def downgrade() -> None:
    """Remove is_saved column from projects table."""
    op.drop_column('projects', 'is_saved')