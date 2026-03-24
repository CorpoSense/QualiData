"""Fix user ID type from Integer to String(36) UUID

Revision ID: fix_user_id_to_uuid
Revises: fix_user_columns
Create Date: 2026-03-24 10:50:00

"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = 'fix_user_id_to_uuid'
down_revision = 'fix_user_columns'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema - change user ID from Integer to String(36) UUID."""
    # Drop foreign key constraints
    op.drop_constraint('projects_owner_id_fkey', 'projects', type_='foreignkey')
    op.drop_constraint('agents_owner_id_fkey', 'agents', type_='foreignkey')
    
    # Add temporary columns for new UUID values
    op.add_column('users', sa.Column('new_id', sa.String(36), nullable=True))
    op.add_column('projects', sa.Column('new_owner_id', sa.String(36), nullable=True))
    op.add_column('agents', sa.Column('new_owner_id', sa.String(36), nullable=True))
    
    # Generate UUIDs for existing users and update references
    conn = op.get_bind()
    
    # Get all users
    result = conn.execute(sa.text("SELECT id FROM users"))
    users = result.fetchall()
    
    # Create mapping of old ID to new UUID
    id_mapping = {}
    for user in users:
        old_id = user[0]
        new_id = str(uuid.uuid4())
        id_mapping[old_id] = new_id
        
        # Update users table
        conn.execute(
            sa.text("UPDATE users SET new_id = :new_id WHERE id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Update projects table
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE projects SET new_owner_id = :new_id WHERE owner_id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Update agents table
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE agents SET new_owner_id = :new_id WHERE owner_id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Drop old columns
    op.drop_column('users', 'id')
    op.drop_column('projects', 'owner_id')
    op.drop_column('agents', 'owner_id')
    
    # Rename new columns to original names
    op.alter_column('users', 'new_id', new_column_name='id')
    op.alter_column('projects', 'new_owner_id', new_column_name='owner_id')
    op.alter_column('agents', 'new_owner_id', new_column_name='owner_id')
    
    # Make id columns NOT NULL and add primary key
    op.alter_column('users', 'id', nullable=False)
    op.alter_column('projects', 'owner_id', nullable=False)
    op.alter_column('agents', 'owner_id', nullable=False)
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # Re-add foreign key constraints
    op.create_foreign_key('projects_owner_id_fkey', 'projects', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('agents_owner_id_fkey', 'agents', 'users', ['owner_id'], ['id'], ondelete='CASCADE')

def downgrade() -> None:
    """Downgrade schema - revert user ID from String(36) to Integer."""
    # Drop foreign key constraints
    op.drop_constraint('projects_owner_id_fkey', 'projects', type_='foreignkey')
    op.drop_constraint('agents_owner_id_fkey', 'agents', type_='foreignkey')
    
    # Add temporary columns for new integer values
    op.add_column('users', sa.Column('new_id', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('new_owner_id', sa.Integer(), nullable=True))
    op.add_column('agents', sa.Column('new_owner_id', sa.Integer(), nullable=True))
    
    # Generate sequential integers for existing users and update references
    conn = op.get_bind()
    
    # Get all users
    result = conn.execute(sa.text("SELECT id FROM users ORDER BY created_at"))
    users = result.fetchall()
    
    # Create mapping of old UUID to new integer ID
    id_mapping = {}
    for idx, user in enumerate(users, start=1):
        old_id = user[0]
        new_id = idx
        id_mapping[old_id] = new_id
        
        # Update users table
        conn.execute(
            sa.text("UPDATE users SET new_id = :new_id WHERE id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Update projects table
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE projects SET new_owner_id = :new_id WHERE owner_id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Update agents table
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE agents SET new_owner_id = :new_id WHERE owner_id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Drop old columns
    op.drop_column('users', 'id')
    op.drop_column('projects', 'owner_id')
    op.drop_column('agents', 'owner_id')
    
    # Rename new columns to original names
    op.alter_column('users', 'new_id', new_column_name='id')
    op.alter_column('projects', 'new_owner_id', new_column_name='owner_id')
    op.alter_column('agents', 'new_owner_id', new_column_name='owner_id')
    
    # Make id columns NOT NULL and add primary key
    op.alter_column('users', 'id', nullable=False)
    op.alter_column('projects', 'owner_id', nullable=False)
    op.alter_column('agents', 'owner_id', nullable=False)
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # Re-add foreign key constraints
    op.create_foreign_key('projects_owner_id_fkey', 'projects', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('agents_owner_id_fkey', 'agents', 'users', ['owner_id'], ['id'], ondelete='CASCADE')