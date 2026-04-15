from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.errors import AppError


load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", case_sensitive=True)

    node_env: str = Field(default="development", alias="NODE_ENV")
    port: int = Field(default=3000, alias="PORT")
    database_url: str = Field(
        default="mysql://linkdb:linkdb_password@localhost:3306/linkdb",
        alias="DATABASE_URL",
    )
    cors_origin: str = Field(default="http://localhost:5173", alias="CORS_ORIGIN")
    json_body_limit: str = Field(default="100kb", alias="JSON_BODY_LIMIT")
    login_rate_limit_window_ms: int = Field(
        default=900000,
        alias="LOGIN_RATE_LIMIT_WINDOW_MS",
    )
    login_rate_limit_max_requests: int = Field(
        default=10,
        alias="LOGIN_RATE_LIMIT_MAX_REQUESTS",
    )
    auth_token_secret: str | None = Field(default=None, alias="AUTH_TOKEN_SECRET")
    auth_cookie_name: str = Field(default="linkdb_session", alias="AUTH_COOKIE_NAME")
    auth_token_ttl_days: int = Field(default=7, alias="AUTH_TOKEN_TTL_DAYS")

    @computed_field
    @property
    def allowed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origin.split(",") if origin.strip()]

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.node_env == "production"

    @computed_field
    @property
    def session_ttl_ms(self) -> int:
        return self.auth_token_ttl_days * 24 * 60 * 60 * 1000

    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("mysql://"):
            return self.database_url.replace("mysql://", "mysql+pymysql://", 1)
        return self.database_url

    def assert_production_secrets(self) -> None:
        if (
            self.is_production
            and self.auth_token_secret == "change-me-in-production"
        ):
            raise AppError(
                "AUTH_CONFIGURATION_ERROR",
                500,
                "AUTH_TOKEN_SECRET must be changed in production.",
            )

    def require_auth_token_secret(self) -> str:
        if not self.auth_token_secret:
            raise AppError(
                "AUTH_CONFIGURATION_ERROR",
                500,
                "AUTH_TOKEN_SECRET is not configured.",
            )
        return self.auth_token_secret


@lru_cache
def get_settings() -> Settings:
    return Settings()
