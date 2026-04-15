def test_links_crud_flow_works_with_session_cookie(client, create_user):
    create_user("mario", "SuperPassword123")
    client.post(
        "/api/auth/login",
        json={"username": "mario", "password": "SuperPassword123"},
    )

    create_response = client.post(
        "/api/links",
        json={
            "title": "Example",
            "link": "https://example.com",
            "description": "A useful example",
            "categories": ["tool", "ai"],
            "status": "working",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["addedBy"]["username"] == "mario"
    assert created["link"] == "https://example.com"
    assert {category["slug"] for category in created["categories"]} == {"tool", "ai"}

    list_response = client.get("/api/links?categories=tool&q=example")
    assert list_response.status_code == 200
    assert list_response.json()["data"]["meta"]["total"] == 1

    update_response = client.patch(
        f"/api/links/{created['id']}",
        json={"title": "Updated Example", "status": "down"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["title"] == "Updated Example"
    assert update_response.json()["data"]["status"] == "down"

    delete_response = client.delete(f"/api/links/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["message"] == "Link deleted successfully."


def test_links_create_requires_valid_body(client, create_user):
    create_user("mario", "SuperPassword123")
    client.post(
        "/api/auth/login",
        json={"username": "mario", "password": "SuperPassword123"},
    )

    response = client.post(
        "/api/links",
        json={
            "title": "",
            "link": "not-a-url",
            "description": "",
            "categories": ["tool", "tool"],
            "status": "working",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
