"""Fix user table columns to match User model

Revision ID: fix_user_columns
Revises: merge_heads
Create Date: 2026-03-24 10:36:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_user_columns'
down_revision = 'merge_heads'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema - rename full_name to name and add missing columns."""
    # Rename full_name to name
    op.alter_column('users', 'full_name', new_column_name='name')
    
    # Add missing columns
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('github_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('storage_used_bytes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('api_calls_this_month', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    
    # Rename last_login to last_login_at
    op.alter_column('users', 'last_login', new_column_name='last_login_at')

def downgrade() -> None:
    """Downgrade schema."""
    # Rename last_login_at back to last_login
    op.alter_column('users', 'last_login_at', new_column_name='last_login')
    
    # Drop added columns
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'api_calls_this_month')
    op.drop_column('users', 'storage_used_bytes')
    op.drop_column('users', 'github_id')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'avatar_url')
    
    # Rename name back to full_name
    op.alter_column('users', 'name', new_column_name='full_name')