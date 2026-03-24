"""Merge migration heads

Revision ID: merge_heads
Revises: add_operation_history_fields, rename_password_column
Create Date: 2026-03-24 10:06:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'merge_heads'
down_revision = ('add_operation_history_fields', 'rename_password_column')
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Merge the two migration branches"""
    pass

def downgrade() -> None:
    """Split the merged branches"""
    pass