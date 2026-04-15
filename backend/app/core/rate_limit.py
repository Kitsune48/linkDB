from collections import defaultdict, deque
from time import time

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import AppError


class LoginRateLimiter:
    def __init__(self) -> None:
        self._attempts: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        settings = get_settings()
        now = time()
        window_seconds = settings.login_rate_limit_window_ms / 1000
        key = request.client.host if request.client else "unknown"
        entries = self._attempts[key]

        while entries and entries[0] <= now - window_seconds:
            entries.popleft()

        if len(entries) >= settings.login_rate_limit_max_requests:
            raise AppError(
                "RATE_LIMITED",
                429,
                "Too many login attempts. Please try again later.",
            )

        entries.append(now)


login_rate_limiter = LoginRateLimiter()
