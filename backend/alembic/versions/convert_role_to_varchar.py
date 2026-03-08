"""Convert role from enum to varchar

Revision ID: convert_role_to_varchar
Revises: add_role_timezone
Create Date: 2026-03-08 10:18:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'convert_role_to_varchar'
down_revision = 'add_role_timezone'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # First, convert all uppercase values to lowercase
    # Handle various formats: ADMIN, UserRole.ADMIN, etc.
    op.execute("""
        UPDATE users SET role = LOWER(
            COALESCE(
                NULLIF(REGEXP_REPLACE(role::text, 'UserRole[.]', '', 'g'), ''),
                role::text
            )
        )
        WHERE role IS NOT NULL
    """)
    
    # Drop the old enum type if it exists
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")
    
    # Recreate as varchar
    op.alter_column('users', 'role',
                   existing_type=sa.Enum('ADMIN', 'MANAGER', 'USER', name='userrole'),
                   type_=sa.String(20),
                   existing_nullable=True,
                   postgresql_using='role::character varying')

def downgrade() -> None:
    pass
