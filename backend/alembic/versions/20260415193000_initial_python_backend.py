"""Initial Python backend schema.

Revision ID: 20260415193000
Revises:
Create Date: 2026-04-15 21:30:00
"""

from alembic import op
import sqlalchemy as sa
from app.db.category_seed import category_rows


revision = "20260415193000"
down_revision = None
branch_labels = None
depends_on = None


link_status_enum = sa.Enum(
    "working",
    "down",
    "unknown",
    "seized",
    name="linkstatus",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=191), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("users_created_at_idx", "users", ["created_at"])
    op.create_index("users_updated_at_idx", "users", ["updated_at"])

    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("link", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", link_status_enum, nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["added_by"],
            ["users.id"],
            name="links_added_by_fkey",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("links_added_by_idx", "links", ["added_by"])
    op.create_index("links_created_at_idx", "links", ["created_at"])
    op.create_index("links_updated_at_idx", "links", ["updated_at"])
    op.create_index("links_status_idx", "links", ["status"])

    op.create_table(
        "_CategoryToLink",
        sa.Column("A", sa.Integer(), nullable=False),
        sa.Column("B", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["A"], ["categories.id"], ondelete="CASCADE", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["B"], ["links.id"], ondelete="CASCADE", onupdate="CASCADE"),
        sa.PrimaryKeyConstraint("A", "B"),
    )
    op.create_index("_CategoryToLink_B_index", "_CategoryToLink", ["B"])

    category_table = sa.table(
        "categories",
        sa.column("slug", sa.String),
        sa.column("label", sa.String),
    )
    op.bulk_insert(category_table, category_rows())


def downgrade() -> None:
    op.drop_index("_CategoryToLink_B_index", table_name="_CategoryToLink")
    op.drop_table("_CategoryToLink")
    op.drop_index("links_status_idx", table_name="links")
    op.drop_index("links_updated_at_idx", table_name="links")
    op.drop_index("links_created_at_idx", table_name="links")
    op.drop_index("links_added_by_idx", table_name="links")
    op.drop_table("links")
    op.drop_index("users_updated_at_idx", table_name="users")
    op.drop_index("users_created_at_idx", table_name="users")
    op.drop_table("users")
    op.drop_table("categories")
