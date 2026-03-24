"""Rename hashed_password column to password_hash in users table

Revision ID: rename_password_column
Revises: convert_role_to_varchar
Create Date: 2026-03-24 09:52:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'rename_password_column'
down_revision = 'convert_role_to_varchar'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Rename hashed_password column to password_hash"""
    # Rename the column
    op.alter_column('users', 'hashed_password', new_column_name='password_hash')


def downgrade() -> None:
    """Rename password_hash column back to hashed_password"""
    # Rename the column back
    op.alter_column('users', 'password_hash', new_column_name='hashed_password')
