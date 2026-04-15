def test_get_auth_me_returns_401_without_cookie(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "UNAUTHENTICATED",
            "message": "Authentication required.",
        },
    }


def test_login_sets_session_cookie_and_returns_user(client, create_user):
    create_user("mario", "SuperPassword123")

    response = client.post(
        "/api/auth/login",
        json={"username": "mario", "password": "SuperPassword123"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["user"]["username"] == "mario"
    assert "createdAt" in response.json()["data"]["user"]
    assert "updatedAt" in response.json()["data"]["user"]
    assert "linkdb_session" in response.cookies


def test_login_rejects_invalid_json_with_expected_error_shape(client):
    response = client.post(
        "/api/auth/login",
        content='{"username"',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "error": {
            "code": "INVALID_JSON",
            "message": "Request body contains invalid JSON.",
        },
    }


def test_auth_me_returns_camel_case_user_fields(client, create_user):
    create_user("mario", "SuperPassword123")
    client.post(
        "/api/auth/login",
        json={"username": "mario", "password": "SuperPassword123"},
    )

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert "createdAt" in response.json()["data"]["user"]
    assert "updatedAt" in response.json()["data"]["user"]
