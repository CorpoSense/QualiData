"""Initial migration - Create MasterDataCleaner tables

Revision ID: 21b545f994e8
Revises:
Create Date: 2026-02-26 13:24:54.987002

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '21b545f994e8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - only create new tables."""
    # Users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=True),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('oauth_provider', sa.String(length=50), nullable=True),
    sa.Column('oauth_id', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Projects table
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('row_count', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('storage_bytes', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['owner_id'], unique=False)

    # Datasets table
    op.create_table('datasets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('file_type', sa.String(length=50), nullable=True),
    sa.Column('preview_data', sa.JSON(), nullable=True),
    sa.Column('columns', sa.JSON(), nullable=True),
    sa.Column('row_count', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_datasets_project_id'), 'datasets', ['project_id'], unique=False)

    # Operation history table
    op.create_table('operation_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('operation_type', sa.String(length=100), nullable=False),
    sa.Column('operation_params', sa.JSON(), nullable=True),
    sa.Column('operation_result', sa.JSON(), nullable=True),
    sa.Column('before_snapshot', sa.JSON(), nullable=True),
    sa.Column('after_snapshot', sa.JSON(), nullable=True),
    sa.Column('is_applied', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('is_undone', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('dataset_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_operation_history_created_at'), 'operation_history', ['created_at'], unique=False)
    op.create_index(op.f('ix_operation_history_project_id'), 'operation_history', ['dataset_id'], unique=False)

    # Agents table
    op.create_table('agents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('provider', sa.String(length=50), nullable=False, server_default='openai'),
    sa.Column('model', sa.String(length=100), nullable=True),
    sa.Column('temperature', sa.Float(), nullable=False, server_default='0.3'),
    sa.Column('system_prompt', sa.Text(), nullable=True),
    sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_user_id'), 'agents', ['owner_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_agents_user_id'), table_name='agents')
    op.drop_table('agents')
    op.drop_index(op.f('ix_operation_history_project_id'), table_name='operation_history')
    op.drop_index(op.f('ix_operation_history_created_at'), table_name='operation_history')
    op.drop_table('operation_history')
    op.drop_index(op.f('ix_datasets_project_id'), table_name='datasets')
    op.drop_table('datasets')
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
