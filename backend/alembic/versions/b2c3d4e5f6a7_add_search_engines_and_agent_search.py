"""add search_engines table and agent.search_engine_id

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-07 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create search_engines table (idempotent — skip if already exists)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "search_engines" not in existing_tables:
        op.create_table(
            "search_engines",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("provider", sa.String(50), nullable=False),
            sa.Column("api_key", sa.Text, nullable=True),
            sa.Column("config", sa.JSON, nullable=True),
            sa.Column("is_builtin", sa.Boolean, default=False),
            sa.Column("created_at", sa.DateTime, default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime,
                default=sa.func.now(),
                onupdate=sa.func.now(),
            ),
        )
        op.create_index("ix_search_engines_user_id", "search_engines", ["user_id"])

    # Add search_engine_id FK to agents table (idempotent — skip if column exists)
    agents_columns = [col["name"] for col in inspector.get_columns("agents")]
    if "search_engine_id" not in agents_columns:
        op.add_column(
            "agents",
            sa.Column(
                "search_engine_id",
                sa.String(36),
                sa.ForeignKey("search_engines.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )


def downgrade() -> None:
    op.drop_column("agents", "search_engine_id")
    op.drop_index("ix_search_engines_user_id", table_name="search_engines")
    op.drop_table("search_engines")
