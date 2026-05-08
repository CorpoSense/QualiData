"""Add memory_config JSON column to agents table

Revision ID: a1b2c3d4e5f6
Revises: 155b9933f705
Create Date: 2026-05-06 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '155b9933f705'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add memory_config column to agents table (idempotent)."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    agents_columns = [col["name"] for col in inspector.get_columns("agents")]
    if "memory_config" not in agents_columns:
        op.add_column('agents', sa.Column('memory_config', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove memory_config column from agents table."""
    op.drop_column('agents', 'memory_config')
