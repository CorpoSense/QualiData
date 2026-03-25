"""Add version column to datasets table

Revision ID: add_version_to_datasets
Revises: fix_all_schema_discrepancies
Create Date: 2026-03-25 18:50:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_version_to_datasets'
down_revision = 'fix_all_schema_discrepancies'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema - add version column to datasets table."""
    
    # Check if version column exists before adding
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('datasets')]
    
    if 'version' not in columns:
        op.add_column('datasets', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    """Downgrade schema - remove version column from datasets table."""
    
    # Check if version column exists before dropping
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('datasets')]
    
    if 'version' in columns:
        op.drop_column('datasets', 'version')