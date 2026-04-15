import pytest

from app.core.errors import AppError
from app.schemas.auth import LoginBody
from app.services.auth import auth_service


def test_login_returns_user_when_credentials_are_valid(db_session, create_user):
    create_user("mario", "SuperPassword123")

    result = auth_service.login(
        db_session,
        LoginBody(username="mario", password="SuperPassword123"),
    )

    assert result.username == "mario"
    assert result.id > 0


def test_login_raises_invalid_credentials_when_password_is_wrong(db_session, create_user):
    create_user("mario", "SuperPassword123")

    with pytest.raises(AppError) as exc:
        auth_service.login(
            db_session,
            LoginBody(username="mario", password="wrong-password"),
        )

    assert exc.value.code == "INVALID_CREDENTIALS"
    assert exc.value.status_code == 401
