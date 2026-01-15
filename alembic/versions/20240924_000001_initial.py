"""initial

Revision ID: 20240924_000001
Revises: 
Create Date: 2024-09-24 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20240924_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("agent_name", sa.String(length=255), nullable=False),
        sa.Column("raw_message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("NEW", "REVIEWED", name="property_status"),
            nullable=False,
            server_default="NEW",
        ),
        sa.Column("assigned_client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("link", sa.Text(), nullable=False, server_default=""),
        sa.Column("address", sa.Text(), nullable=False, server_default=""),
        sa.Column("size", sa.Text(), nullable=False, server_default=""),
        sa.Column("price", sa.Text(), nullable=False, server_default=""),
        sa.Column("beds", sa.Text(), nullable=False, server_default=""),
        sa.Column("baths", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(["assigned_client_id"], ["clients.id"]),
    )


def downgrade() -> None:
    op.drop_table("properties")
    op.drop_table("clients")
    op.execute("DROP TYPE IF EXISTS property_status")
