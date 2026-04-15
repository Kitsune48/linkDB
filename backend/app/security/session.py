import base64
import hashlib
import hmac
import json
from time import time

from app.core.config import get_settings
from app.core.errors import AppError
from app.schemas.common import SessionUser


def _base64url_encode(value: str) -> str:
    encoded = base64.urlsafe_b64encode(value.encode("utf-8")).decode("utf-8")
    return encoded.rstrip("=")


def _base64url_decode(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("utf-8")).decode("utf-8")


def _sign_value(value: str, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def create_session_token(user_id: int, username: str) -> str:
    settings = get_settings()
    secret = settings.require_auth_token_secret()
    payload = {
        "sub": user_id,
        "username": username,
        "exp": int((time() * 1000 + settings.session_ttl_ms) / 1000),
    }
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")))
    signature = _sign_value(encoded_payload, secret)
    return f"{encoded_payload}.{signature}"


def verify_session_token(token: str) -> SessionUser:
    settings = get_settings()
    secret = settings.require_auth_token_secret()
    encoded_payload, separator, signature = token.partition(".")
    if not encoded_payload or not separator or not signature:
        raise AppError("UNAUTHENTICATED", 401, "Authentication required.")

    expected_signature = _sign_value(encoded_payload, secret)
    if not hmac.compare_digest(signature, expected_signature):
        raise AppError("UNAUTHENTICATED", 401, "Authentication required.")

    payload = json.loads(_base64url_decode(encoded_payload))
    if payload["exp"] * 1000 <= time() * 1000:
        raise AppError("UNAUTHENTICATED", 401, "Authentication required.")

    return SessionUser(id=payload["sub"], username=payload["username"])


def session_cookie_options() -> dict[str, object]:
    settings = get_settings()
    return {
        "httponly": True,
        "samesite": "lax",
        "secure": settings.is_production,
        "max_age": settings.session_ttl_ms // 1000,
        "path": "/",
    }
