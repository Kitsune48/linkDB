"""Add read later links.

Revision ID: 20260415210000
Revises: 20260415193000
Create Date: 2026-04-15 21:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415210000"
down_revision = "20260415193000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "read_later_links",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("link_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["link_id"], ["links.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "link_id"),
    )
    op.create_index("read_later_links_link_id_idx", "read_later_links", ["link_id"])


def downgrade() -> None:
    op.drop_index("read_later_links_link_id_idx", table_name="read_later_links")
    op.drop_table("read_later_links")
