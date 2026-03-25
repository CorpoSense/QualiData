"""Fix agents table: rename owner_id to user_id

Revision ID: fix_agents_owner_id_to_user_id
Revises: add_is_saved_to_projects
Create Date: 2026-03-25 13:40:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_agents_owner_id_to_user_id'
down_revision = 'add_is_saved_to_projects'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Rename owner_id to user_id in agents table."""
    # Check if owner_id column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('agents')]
    
    if 'owner_id' in columns:
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

def downgrade() -> None:
    """Revert user_id back to owner_id in agents table."""
    # Check if user_id column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('agents')]
    
    if 'user_id' in columns:
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