import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["AUTH_TOKEN_SECRET"] = "test-secret"
os.environ["CORS_ORIGIN"] = "http://localhost:5173"
os.environ["NODE_ENV"] = "development"

from app.db.base import Base
from app.db.category_seed import category_rows
from app.db.models import Category, User
from app.db.session import get_db_session
from app.main import app
from app.security.password import hash_password


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    session.add_all([Category(**row) for row in category_rows()])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(db_session: Session):
    def factory(username: str, password: str = "SuperPassword123") -> User:
        user = User(username=username, password=hash_password(password))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return factory
