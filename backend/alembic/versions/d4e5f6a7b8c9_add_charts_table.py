"""add charts table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-13 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "charts" not in existing_tables:
        op.create_table(
            "charts",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "dataset_id",
                sa.String(36),
                sa.ForeignKey("datasets.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("config", sa.JSON, nullable=False),
            sa.Column("meta", sa.JSON, nullable=True),
            sa.Column("sort_order", sa.Integer, default=0),
            sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        )
        op.create_index("ix_charts_dataset_id", "charts", ["dataset_id"])


def downgrade() -> None:
    op.drop_index("ix_charts_dataset_id", table_name="charts")
    op.drop_table("charts")