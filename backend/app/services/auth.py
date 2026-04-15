from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import User
from app.schemas.auth import LoginBody
from app.schemas.common import SessionUser, UserOut
from app.security.password import verify_password

INVALID_CREDENTIALS_MESSAGE = "Invalid username or password."
UNAUTHENTICATED_MESSAGE = "Authentication required."


class AuthService:
    def login(self, db: Session, input_data: LoginBody) -> UserOut:
        user = db.scalar(select(User).where(User.username == input_data.username))
        if user is None or not verify_password(input_data.password, user.password):
            raise AppError("INVALID_CREDENTIALS", 401, INVALID_CREDENTIALS_MESSAGE)
        return UserOut.model_validate(user)

    def get_current_user(self, db: Session, session_user: SessionUser | None) -> UserOut:
        if session_user is None:
            raise AppError("UNAUTHENTICATED", 401, UNAUTHENTICATED_MESSAGE)

        user = db.scalar(select(User).where(User.id == session_user.id))
        if user is None:
            raise AppError("UNAUTHENTICATED", 401, UNAUTHENTICATED_MESSAGE)
        return UserOut.model_validate(user)


auth_service = AuthService()
