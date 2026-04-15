from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.db.models import User
from app.db.session import get_db_session
from app.schemas.common import SessionUser
from app.security.session import verify_session_token


def require_auth(
    db: Annotated[Session, Depends(get_db_session)],
    session_token: Annotated[str | None, Cookie(alias=get_settings().auth_cookie_name)] = None,
) -> SessionUser:
    if not session_token:
        raise AppError("UNAUTHENTICATED", 401, "Authentication required.")

    session_user = verify_session_token(session_token)
    user = db.get(User, session_user.id)
    if user is None:
        raise AppError("UNAUTHENTICATED", 401, "Authentication required.")

    return SessionUser(id=user.id, username=user.username)
