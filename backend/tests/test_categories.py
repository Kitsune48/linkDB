import os
from pathlib import Path
import subprocess
import sys

import pytest

from app.core.errors import AppError
from app.schemas.categories import CreateCategoryInput
from app.services.categories import categories_service


def test_list_categories_route_returns_catalog_for_authenticated_user(client, create_user):
    create_user("mario", "SuperPassword123")
    client.post(
        "/api/auth/login",
        json={"username": "mario", "password": "SuperPassword123"},
    )

    response = client.get("/api/categories")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert any(category["slug"] == "tool" for category in payload)
    assert any(category["label"] == "AI" for category in payload)


def test_create_category_service_creates_new_category(db_session):
    category = categories_service.create_category(
        db_session,
        CreateCategoryInput(slug="search-engine", label="Search Engine"),
    )

    assert category.slug == "search-engine"
    assert category.label == "Search Engine"


def test_create_category_service_rejects_duplicate_slug(db_session):
    categories_service.create_category(
        db_session,
        CreateCategoryInput(slug="search-engine", label="Search Engine"),
    )

    with pytest.raises(AppError) as exc:
        categories_service.create_category(
            db_session,
            CreateCategoryInput(slug="search-engine", label="Another Label"),
        )

    assert exc.value.code == "CATEGORY_ALREADY_EXISTS"
    assert exc.value.status_code == 409


def test_create_category_cli_creates_category_against_temp_sqlite():
    database_path = Path("C:/Users/gigi/Desktop/linkDB/backend/.cli-categories-test.db")
    if database_path.exists():
        database_path.unlink()
    env = os.environ | {
        "DATABASE_URL": f"sqlite+pysqlite:///{database_path.as_posix()}",
        "AUTH_TOKEN_SECRET": "test-secret",
    }

    migration = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd="C:\\Users\\gigi\\Desktop\\linkDB\\backend",
        env=env,
        capture_output=True,
        text=True,
    )
    assert migration.returncode == 0, migration.stderr

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.scripts.create_category",
            "search-engine",
            "Search Engine",
        ],
        cwd="C:\\Users\\gigi\\Desktop\\linkDB\\backend",
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Category created successfully." in result.stdout
    if database_path.exists():
        database_path.unlink()
