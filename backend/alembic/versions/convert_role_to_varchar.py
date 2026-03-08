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
    # Update any existing values to string
    op.execute("""
        UPDATE users SET role = LOWER(REGEXP_REPLACE(role::text, 'UserRole[.]', ''))
        WHERE role IS NOT NULL
    """)
    
    # Alter the column type using ALTER COLUMN
    op.alter_column('users', 'role',
                   existing_type=sa.String(20),
                   type_=sa.String(20),
                   existing_nullable=True,
                   postgresql_using='role::character varying')

def downgrade() -> None:
    pass
