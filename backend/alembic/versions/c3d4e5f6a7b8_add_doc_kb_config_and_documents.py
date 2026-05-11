"""add doc_kb_config to agents and documents table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-11 11:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Add doc_kb_config JSON column to agents (idempotent)
    agents_columns = [col["name"] for col in inspector.get_columns("agents")]
    if "doc_kb_config" not in agents_columns:
        op.add_column(
            "agents",
            sa.Column("doc_kb_config", sa.JSON, nullable=True),
        )

    # Create documents table (idempotent — skip if already exists)
    if "documents" not in existing_tables:
        op.create_table(
            "documents",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "agent_id",
                sa.String(36),
                sa.ForeignKey("agents.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("filename", sa.String(255), nullable=False),
            sa.Column("content_type", sa.String(100), nullable=False),
            sa.Column("file_type", sa.String(20), nullable=False),
            sa.Column("size_bytes", sa.Integer, nullable=False),
            sa.Column("file_path", sa.String(500), nullable=False),
            sa.Column("status", sa.String(20), default="uploaded"),
            sa.Column("chunk_count", sa.Integer, default=0),
            sa.Column("error_message", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime, default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime,
                default=sa.func.now(),
                onupdate=sa.func.now(),
            ),
            sa.Column("expires_at", sa.DateTime, nullable=True),
        )
        op.create_index("ix_documents_user_id", "documents", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")
    op.drop_column("agents", "doc_kb_config")
