"""Add operation history fields for snapshots

Revision ID: add_operation_history_fields
Revises: add_role_timezone
Create Date: 2026-03-09 12:05:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_operation_history_fields'
down_revision = 'add_role_timezone'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add operation_params JSON column
    op.add_column('operation_history', sa.Column('operation_params', sa.JSON(), nullable=True))
    
    # Add is_undone boolean column
    op.add_column('operation_history', sa.Column('is_undone', sa.Boolean(), nullable=True, server_default='false'))
    
    # Add is_applied boolean column  
    op.add_column('operation_history', sa.Column('is_applied', sa.Boolean(), nullable=True, server_default='true'))
    
    # Add before_snapshot JSON column
    op.add_column('operation_history', sa.Column('before_snapshot', sa.JSON(), nullable=True))
    
    # Add after_snapshot JSON column
    op.add_column('operation_history', sa.Column('after_snapshot', sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column('operation_history', 'after_snapshot')
    op.drop_column('operation_history', 'before_snapshot')
    op.drop_column('operation_history', 'is_applied')
    op.drop_column('operation_history', 'is_undone')
    op.drop_column('operation_history', 'operation_params')
