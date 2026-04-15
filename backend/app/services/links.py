from math import ceil

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppError
from app.db.models import Category, Link
from app.schemas.links import (
    CreateLinkBody,
    LinkOut,
    ListLinksQuery,
    PaginatedLinksResponse,
    UpdateLinkBody,
)


SORT_FIELD_MAP = {
    "createdAt": Link.created_at,
    "updatedAt": Link.updated_at,
    "title": Link.title,
}


class LinksService:
    def list_links(
        self,
        db: Session,
        query: ListLinksQuery,
        current_user_id: int | None = None,
    ) -> PaginatedLinksResponse:
        filters = []
        if query.q:
            pattern = f"%{query.q}%"
            filters.append(
                or_(
                    Link.title.like(pattern),
                    Link.description.like(pattern),
                    Link.link.like(pattern),
                )
            )

        selected_categories = query.selected_categories()
        if selected_categories:
            filters.append(Link.categories.any(Category.slug.in_(selected_categories)))

        if query.status:
            filters.append(Link.status == query.status)

        if query.added_by:
            filters.append(Link.added_by_id == query.added_by)

        statement = (
            select(Link)
            .options(
                joinedload(Link.categories),
                joinedload(Link.added_by),
                joinedload(Link.saved_by_users),
            )
            .where(*filters)
        )
        sort_field = SORT_FIELD_MAP[query.sort]
        statement = statement.order_by(
            sort_field.asc() if query.order == "asc" else sort_field.desc()
        )
        statement = statement.offset((query.page - 1) * query.limit).limit(query.limit)

        count_statement = select(func.count(Link.id)).where(*filters)
        items = db.scalars(statement).unique().all()
        total = db.scalar(count_statement) or 0

        return PaginatedLinksResponse(
            items=[self.serialize_link(item, current_user_id=current_user_id) for item in items],
            meta={
                "page": query.page,
                "limit": query.limit,
                "total": total,
                "totalPages": max(1, ceil(total / query.limit)),
            },
        )

    def get_link_by_id(
        self,
        db: Session,
        link_id: int,
        current_user_id: int | None = None,
    ) -> LinkOut:
        link = db.scalar(
            select(Link)
            .options(
                joinedload(Link.categories),
                joinedload(Link.added_by),
                joinedload(Link.saved_by_users),
            )
            .where(Link.id == link_id)
        )
        if link is None:
            raise AppError("LINK_NOT_FOUND", 404, "Link not found.")
        return self.serialize_link(link, current_user_id=current_user_id)

    def create_link(self, db: Session, input_data: CreateLinkBody, user_id: int) -> LinkOut:
        link = Link(
            link=str(input_data.link),
            title=input_data.title,
            description=input_data.description,
            status=input_data.status,
            added_by_id=user_id,
            categories=self._get_categories(db, input_data.categories),
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return self.get_link_by_id(db, link.id, current_user_id=user_id)

    def update_link(
        self,
        db: Session,
        link_id: int,
        input_data: UpdateLinkBody,
        user_id: int,
    ) -> LinkOut:
        link = db.scalar(
            select(Link)
            .options(joinedload(Link.categories), joinedload(Link.added_by))
            .where(Link.id == link_id)
        )
        if link is None:
            raise AppError("LINK_NOT_FOUND", 404, "Link not found.")
        if link.added_by_id != user_id:
            raise AppError("FORBIDDEN", 403, "You can only modify your own links.")

        payload = input_data.model_dump(exclude_none=True)
        if "link" in payload:
            link.link = str(payload["link"])
        if "title" in payload:
            link.title = payload["title"]
        if "description" in payload:
            link.description = payload["description"]
        if "status" in payload:
            link.status = payload["status"]
        if "categories" in payload:
            link.categories = self._get_categories(db, payload["categories"])

        db.commit()
        db.refresh(link)
        return self.get_link_by_id(db, link.id, current_user_id=user_id)

    def delete_link(self, db: Session, link_id: int, user_id: int) -> None:
        link = db.scalar(select(Link).where(Link.id == link_id))
        if link is None:
            raise AppError("LINK_NOT_FOUND", 404, "Link not found.")
        if link.added_by_id != user_id:
            raise AppError("FORBIDDEN", 403, "You can only delete your own links.")
        db.delete(link)
        db.commit()

    def _get_categories(
        self,
        db: Session,
        categories: list[str],
    ) -> list[Category]:
        slugs = categories
        rows = db.scalars(select(Category).where(Category.slug.in_(slugs))).all()
        if len(rows) != len(slugs):
            raise AppError("VALIDATION_ERROR", 400, "Request validation failed.")
        by_slug = {row.slug: row for row in rows}
        return [by_slug[slug] for slug in slugs]

    def serialize_link(self, link: Link, current_user_id: int | None = None) -> LinkOut:
        link.categories = sorted(link.categories, key=lambda category: category.slug)
        payload = LinkOut.model_validate(link)
        payload.is_in_read_later = (
            current_user_id is not None
            and any(user.id == current_user_id for user in link.saved_by_users)
        )
        return payload


links_service = LinksService()
