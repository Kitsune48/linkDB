from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppError
from app.db.models import Link, User
from app.schemas.links import LinkOut
from app.services.links import links_service


class ReadLaterService:
    def list_read_later_links(self, db: Session, user_id: int) -> list[LinkOut]:
        user = db.scalar(
            select(User)
            .options(
                joinedload(User.read_later_links).joinedload(Link.categories),
                joinedload(User.read_later_links).joinedload(Link.added_by),
            )
            .where(User.id == user_id)
        )
        if user is None:
            raise AppError("UNAUTHENTICATED", 401, "Authentication required.")

        links = sorted(user.read_later_links, key=lambda link: link.updated_at, reverse=True)
        return [links_service.serialize_link(link, current_user_id=user_id) for link in links]

    def add_to_read_later(self, db: Session, user_id: int, link_id: int) -> LinkOut:
        user = db.scalar(
            select(User)
            .options(joinedload(User.read_later_links))
            .where(User.id == user_id)
        )
        link = db.scalar(
            select(Link)
            .options(joinedload(Link.categories), joinedload(Link.added_by), joinedload(Link.saved_by_users))
            .where(Link.id == link_id)
        )
        if user is None:
            raise AppError("UNAUTHENTICATED", 401, "Authentication required.")
        if link is None:
            raise AppError("LINK_NOT_FOUND", 404, "Link not found.")

        if not any(saved.id == link.id for saved in user.read_later_links):
            user.read_later_links.append(link)
            db.commit()
            db.refresh(link)

        return links_service.get_link_by_id(db, link_id, current_user_id=user_id)

    def remove_from_read_later(self, db: Session, user_id: int, link_id: int) -> None:
        user = db.scalar(
            select(User)
            .options(joinedload(User.read_later_links))
            .where(User.id == user_id)
        )
        if user is None:
            raise AppError("UNAUTHENTICATED", 401, "Authentication required.")

        link = next((item for item in user.read_later_links if item.id == link_id), None)
        if link is None:
            raise AppError("LINK_NOT_FOUND", 404, "Link not found.")

        user.read_later_links.remove(link)
        db.commit()


read_later_service = ReadLaterService()
