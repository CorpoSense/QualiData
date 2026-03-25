"""Fix all schema discrepancies between models and database

Revision ID: fix_all_schema_discrepancies
Revises: fix_user_id_to_uuid
Create Date: 2026-03-24 11:57:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_all_schema_discrepancies'
down_revision = 'fix_user_id_to_uuid'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema - fix all discrepancies between models and database."""
    
    # ============================================
    # 1. FIX PROJECTS TABLE
    # ============================================
    
    # Drop foreign key constraints first
    op.drop_constraint('datasets_project_id_fkey', 'datasets', type_='foreignkey')
    op.drop_constraint('operation_history_dataset_id_fkey', 'operation_history', type_='foreignkey')
    
    # Change projects.id from Integer to String(36) to match model
    op.alter_column('projects', 'id',
                   existing_type=sa.Integer(),
                   type_=sa.String(36),
                   existing_nullable=False)
    
    # Add missing column_count column
    op.add_column('projects', sa.Column('column_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Change storage_bytes from Integer to BigInteger
    op.alter_column('projects', 'storage_bytes',
                   existing_type=sa.Integer(),
                   type_=sa.BigInteger(),
                   existing_nullable=False)
    
    # Check if owner_id exists and rename to user_id
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]
    
    if 'owner_id' in columns:
        # Rename owner_id to user_id
        op.alter_column('projects', 'owner_id', new_column_name='user_id')
    
    # Handle index - check if it exists and update accordingly
    indexes = [idx['name'] for idx in inspector.get_indexes('projects')]
    
    # Drop old index if it exists
    if 'ix_projects_user_id' in indexes:
        op.drop_index('ix_projects_user_id', table_name='projects')
    
    # Create new index on user_id
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])
    
    # ============================================
    # 2. FIX DATASETS TABLE
    # ============================================
    
    # Change datasets.id from Integer to String(36) to match model
    op.alter_column('datasets', 'id',
                   existing_type=sa.Integer(),
                   type_=sa.String(36),
                   existing_nullable=False)
    
    # Change datasets.project_id from Integer to String(36) to match projects.id
    op.alter_column('datasets', 'project_id',
                   existing_type=sa.Integer(),
                   type_=sa.String(36),
                   existing_nullable=False)
    
    # Add missing data_json column
    op.add_column('datasets', sa.Column('data_json', sa.JSON(), nullable=True))
    
    # Add missing schema_json column
    op.add_column('datasets', sa.Column('schema_json', sa.JSON(), nullable=True))
    
    # ============================================
    # 3. FIX OPERATION_HISTORY TABLE
    # ============================================
    
    # Change dataset_id from Integer to String(36) to match datasets.id
    op.alter_column('operation_history', 'dataset_id',
                   existing_type=sa.Integer(),
                   type_=sa.String(36),
                   existing_nullable=True)
    
    # Add missing project_id column with foreign key
    op.add_column('operation_history', sa.Column('project_id', sa.String(36), nullable=True))
    op.create_foreign_key('operation_history_project_id_fkey', 'operation_history', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    
    # Check if index exists before creating
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = [idx['name'] for idx in inspector.get_indexes('operation_history')]
    
    if 'ix_operation_history_project_id' not in indexes:
        op.create_index('ix_operation_history_project_id', 'operation_history', ['project_id'])
    
    # Re-add foreign key constraints
    op.create_foreign_key('datasets_project_id_fkey', 'datasets', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('operation_history_dataset_id_fkey', 'operation_history', 'datasets', ['dataset_id'], ['id'], ondelete='CASCADE')
    
    # Add missing operation_name column
    op.add_column('operation_history', sa.Column('operation_name', sa.String(100), nullable=True))
    
    # Add missing operation_config column
    op.add_column('operation_history', sa.Column('operation_config', sa.JSON(), nullable=True))
    
    # Add missing columns_affected column
    op.add_column('operation_history', sa.Column('columns_affected', sa.JSON(), nullable=True))
    
    # Add missing snapshot_json column
    op.add_column('operation_history', sa.Column('snapshot_json', sa.JSON(), nullable=True))
    
    # ============================================
    # 4. FIX AGENTS TABLE
    # ============================================
    
    # Check if columns exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    agent_columns = [c['name'] for c in inspector.get_columns('agents')]
    
    # Check if owner_id exists and rename to user_id
    if 'owner_id' in agent_columns:
        # Drop foreign key constraint first
        op.drop_constraint('agents_owner_id_fkey', 'agents', type_='foreignkey')
        # Rename owner_id to user_id
        op.alter_column('agents', 'owner_id', new_column_name='user_id')
        # Re-create foreign key constraint with new column name
        op.create_foreign_key('agents_user_id_fkey', 'agents', 'users', ['user_id'], ['id'], ondelete='CASCADE')
        # Update index if it exists
        indexes = [idx['name'] for idx in inspector.get_indexes('agents')]
        if 'ix_agents_owner_id' in indexes:
            op.drop_index('ix_agents_owner_id', table_name='agents')
        op.create_index('ix_agents_user_id', 'agents', ['user_id'])
    
    # Add missing prompt_template column
    if 'prompt_template' not in agent_columns:
        op.add_column('agents', sa.Column('prompt_template', sa.Text(), nullable=True))
    
    # Add missing api_key column
    if 'api_key' not in agent_columns:
        op.add_column('agents', sa.Column('api_key', sa.Text(), nullable=True))
    
    # Add missing base_url column
    if 'base_url' not in agent_columns:
        op.add_column('agents', sa.Column('base_url', sa.String(500), nullable=True))
    
    # Add missing is_builtin column
    if 'is_builtin' not in agent_columns:
        op.add_column('agents', sa.Column('is_builtin', sa.Boolean(), nullable=False, server_default='false'))
    
    # Drop unused usage_count column if it exists
    if 'usage_count' in agent_columns:
        op.drop_column('agents', 'usage_count')
    
    # Make model column non-nullable with default
    op.alter_column('agents', 'model',
                   existing_type=sa.String(100),
                   nullable=False,
                   server_default='gpt-4o-mini')


def downgrade() -> None:
    """Downgrade schema - revert all changes."""
    
    # ============================================
    # 4. REVERT AGENTS TABLE
    # ============================================
    
    # Revert model column to nullable
    op.alter_column('agents', 'model',
                   existing_type=sa.String(100),
                   nullable=True,
                   server_default=None)
    
    # Restore usage_count column
    op.add_column('agents', sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Drop added columns
    op.drop_column('agents', 'is_builtin')
    op.drop_column('agents', 'base_url')
    op.drop_column('agents', 'api_key')
    op.drop_column('agents', 'prompt_template')
    
    # Check if user_id exists and rename back to owner_id
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    agent_columns = [c['name'] for c in inspector.get_columns('agents')]
    
    if 'user_id' in agent_columns:
        # Drop foreign key constraint first
        op.drop_constraint('agents_user_id_fkey', 'agents', type_='foreignkey')
        # Rename user_id back to owner_id
        op.alter_column('agents', 'user_id', new_column_name='owner_id')
        # Re-create foreign key constraint with original column name
        op.create_foreign_key('agents_owner_id_fkey', 'agents', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
        # Update index if it exists
        indexes = [idx['name'] for idx in inspector.get_indexes('agents')]
        if 'ix_agents_user_id' in indexes:
            op.drop_index('ix_agents_user_id', table_name='agents')
        op.create_index('ix_agents_owner_id', 'agents', ['owner_id'])
    
    # ============================================
    # 3. REVERT OPERATION_HISTORY TABLE
    # ============================================
    
    # Drop added columns
    op.drop_column('operation_history', 'snapshot_json')
    op.drop_column('operation_history', 'columns_affected')
    op.drop_column('operation_history', 'operation_config')
    op.drop_column('operation_history', 'operation_name')
    
    # Drop project_id column and constraints
    op.drop_index('ix_operation_history_project_id', table_name='operation_history')
    op.drop_constraint('operation_history_project_id_fkey', 'operation_history', type_='foreignkey')
    op.drop_column('operation_history', 'project_id')
    
    # Revert dataset_id from String(36) to Integer
    op.alter_column('operation_history', 'dataset_id',
                   existing_type=sa.String(36),
                   type_=sa.Integer(),
                   existing_nullable=True)
    
    # ============================================
    # 2. REVERT DATASETS TABLE
    # ============================================
    
    # Drop added columns
    op.drop_column('datasets', 'schema_json')
    op.drop_column('datasets', 'data_json')
    
    # Revert datasets.id from String(36) to Integer
    op.alter_column('datasets', 'id',
                   existing_type=sa.String(36),
                   type_=sa.Integer(),
                   existing_nullable=False)
    
    # Revert datasets.project_id from String(36) to Integer
    op.alter_column('datasets', 'project_id',
                   existing_type=sa.String(36),
                   type_=sa.Integer(),
                   existing_nullable=False)
    
    # ============================================
    # 1. REVERT PROJECTS TABLE
    # ============================================
    
    # Handle index - check if it exists and update accordingly
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = [idx['name'] for idx in inspector.get_indexes('projects')]
    
    # Drop new index if it exists
    if 'ix_projects_user_id' in indexes:
        op.drop_index('ix_projects_user_id', table_name='projects')
    
    # Check if user_id exists and rename back to owner_id
    columns = [c['name'] for c in inspector.get_columns('projects')]
    if 'user_id' in columns:
        op.alter_column('projects', 'user_id', new_column_name='owner_id')
    
    # Create index on owner_id
    op.create_index('ix_projects_user_id', 'projects', ['owner_id'])
    
    # Revert storage_bytes from BigInteger to Integer
    op.alter_column('projects', 'storage_bytes',
                   existing_type=sa.BigInteger(),
                   type_=sa.Integer(),
                   existing_nullable=False)
    
    # Drop column_count column
    op.drop_column('projects', 'column_count')
    
    # Revert projects.id from String(36) to Integer
    op.alter_column('projects', 'id',
                   existing_type=sa.String(36),
                   type_=sa.Integer(),
                   existing_nullable=False)
    
    # Re-add foreign key constraints
    op.create_foreign_key('datasets_project_id_fkey', 'datasets', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('operation_history_dataset_id_fkey', 'operation_history', 'datasets', ['dataset_id'], ['id'], ondelete='CASCADE')