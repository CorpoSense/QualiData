"""Add role and timezone to user

Revision ID: add_role_timezone
Revises: 21b545f994e8
Create Date: 2026-03-07 15:25:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_role_timezone'
down_revision = '21b545f994e8'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(20), nullable=True, server_default='user'))
    op.add_column('users', sa.Column('timezone', sa.String(50), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'role')
