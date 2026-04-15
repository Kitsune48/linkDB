from datetime import datetime

from sqlalchemy import Column, Enum, ForeignKey, Index, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.constants import LinkStatus


category_to_link_table = Table(
    "_CategoryToLink",
    Base.metadata,
    Column("A", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    Column("B", Integer, ForeignKey("links.id", ondelete="CASCADE"), primary_key=True),
)

read_later_link_table = Table(
    "read_later_links",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("link_id", Integer, ForeignKey("links.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    label: Mapped[str] = mapped_column(String(128))
    links: Mapped[list["Link"]] = relationship(
        secondary=category_to_link_table,
        back_populates="categories",
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("users_created_at_idx", "created_at"),
        Index("users_updated_at_idx", "updated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(191), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    links: Mapped[list["Link"]] = relationship(back_populates="added_by")
    read_later_links: Mapped[list["Link"]] = relationship(
        secondary=read_later_link_table,
        back_populates="saved_by_users",
    )


class Link(Base):
    __tablename__ = "links"
    __table_args__ = (
        Index("links_added_by_idx", "added_by"),
        Index("links_created_at_idx", "created_at"),
        Index("links_updated_at_idx", "updated_at"),
        Index("links_status_idx", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    link: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[LinkStatus] = mapped_column(
        Enum(
            LinkStatus,
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
    )
    added_by_id: Mapped[int] = mapped_column(
        "added_by",
        ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    added_by: Mapped[User] = relationship(back_populates="links")
    categories: Mapped[list[Category]] = relationship(
        secondary=category_to_link_table,
        back_populates="links",
    )
    saved_by_users: Mapped[list[User]] = relationship(
        secondary=read_later_link_table,
        back_populates="read_later_links",
    )
