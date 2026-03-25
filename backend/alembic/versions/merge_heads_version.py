"""Merge heads: add_version_to_datasets and fix_agents_owner_id_to_user_id

Revision ID: merge_heads_version
Revises: add_version_to_datasets, fix_agents_owner_id_to_user_id
Create Date: 2026-03-25 19:45:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'merge_heads_version'
down_revision = ('add_version_to_datasets', 'fix_agents_owner_id_to_user_id')
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema - merge migration heads."""
    pass


def downgrade() -> None:
    """Downgrade schema - no-op for merge migration."""
    pass