import pytest

from app.core.errors import AppError
from app.db.models import Link
from app.domain.constants import LinkStatus
from app.schemas.links import CreateLinkBody, ListLinksQuery, UpdateLinkBody
from app.services.links import links_service


def test_create_link_for_authenticated_user(db_session, create_user):
    user = create_user("mario")

    result = links_service.create_link(
        db_session,
        CreateLinkBody(
            title="Example",
            link="https://example.com",
            description="A useful example",
            categories=["tool"],
            status="working",
        ),
        user.id,
    )

    assert result.title == "Example"
    assert result.link == "https://example.com"
    assert [category.slug for category in result.categories] == ["tool"]
    assert result.added_by.id == user.id


def test_update_link_when_current_user_is_owner(db_session, create_user):
    user = create_user("mario")
    created = links_service.create_link(
        db_session,
        CreateLinkBody(
            title="Example",
            link="https://example.com",
            description="A useful example",
            categories=["tool"],
            status="working",
        ),
        user.id,
    )

    result = links_service.update_link(
        db_session,
        created.id,
        UpdateLinkBody(title="Updated title"),
        user.id,
    )

    assert result.title == "Updated title"


def test_reject_update_when_current_user_is_not_owner(db_session, create_user):
    owner = create_user("owner")
    other_user = create_user("other")
    created = links_service.create_link(
        db_session,
        CreateLinkBody(
            title="Example",
            link="https://example.com",
            description="A useful example",
            categories=["tool"],
            status="working",
        ),
        owner.id,
    )

    with pytest.raises(AppError) as exc:
        links_service.update_link(
            db_session,
            created.id,
            UpdateLinkBody(title="Updated title"),
            other_user.id,
        )

    assert exc.value.code == "FORBIDDEN"
    assert exc.value.status_code == 403


def test_delete_link_when_current_user_is_owner(db_session, create_user):
    user = create_user("mario")
    created = links_service.create_link(
        db_session,
        CreateLinkBody(
            title="Example",
            link="https://example.com",
            description="A useful example",
            categories=["tool"],
            status="working",
        ),
        user.id,
    )

    links_service.delete_link(db_session, created.id, user.id)

    assert db_session.get(Link, created.id) is None


def test_apply_search_filters_and_pagination_when_listing_links(db_session, create_user):
    user = create_user("mario")
    links_service.create_link(
        db_session,
        CreateLinkBody(
            title="Proxy list",
            link="https://example.com/proxy",
            description="Forum resource",
            categories=["forum", "ai"],
            status="working",
        ),
        user.id,
    )
    links_service.create_link(
        db_session,
        CreateLinkBody(
            title="Other",
            link="https://example.com/other",
            description="Different",
            categories=["tool"],
            status="down",
        ),
        user.id,
    )

    result = links_service.list_links(
        db_session,
        ListLinksQuery(
            q="proxy",
            categories=["forum", "ai"],
            status=LinkStatus.WORKING,
            addedBy=user.id,
            page=1,
            limit=5,
            sort="updatedAt",
            order="desc",
        ),
    )

    assert len(result.items) == 1
    assert result.items[0].title == "Proxy list"
    assert result.meta.total == 1
    assert result.meta.total_pages == 1


def test_get_link_by_id_raises_not_found_for_unknown_link(db_session):
    with pytest.raises(AppError) as exc:
        links_service.get_link_by_id(db_session, 999)

    assert exc.value.code == "LINK_NOT_FOUND"
    assert exc.value.status_code == 404
