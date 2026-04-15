from app.db.models import Link
from app.schemas.links import CreateLinkBody, ListLinksQuery
from app.services.links import links_service


def test_links_list_marks_items_saved_for_current_user(db_session, create_user):
    user = create_user("mario")
    link = links_service.create_link(
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

    user.read_later_links.append(db_session.get(Link, link.id))
    db_session.commit()

    result = links_service.list_links(
        db_session,
        ListLinksQuery(),
        current_user_id=user.id,
    )

    assert result.items[0].is_in_read_later is True


def test_read_later_route_flow(client, create_user):
    create_user("mario", "SuperPassword123")
    create_response = client.post(
        "/api/auth/login",
        json={"username": "mario", "password": "SuperPassword123"},
    )
    assert create_response.status_code == 200

    link_response = client.post(
        "/api/links",
        json={
            "title": "Example",
            "link": "https://example.com",
            "description": "A useful example",
            "categories": ["tool"],
            "status": "working",
        },
    )
    link_id = link_response.json()["data"]["id"]

    add_response = client.post(f"/api/read-later/{link_id}")
    assert add_response.status_code == 201
    assert add_response.json()["data"]["isInReadLater"] is True

    list_response = client.get("/api/read-later")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1
    assert list_response.json()["data"][0]["id"] == link_id

    remove_response = client.delete(f"/api/read-later/{link_id}")
    assert remove_response.status_code == 200
    assert remove_response.json()["data"]["message"] == "Removed from read later."
