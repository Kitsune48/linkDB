from pydantic import BaseModel, Field, field_validator

from app.schemas.common import UserOut


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=191)
    password: str = Field(min_length=1, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("This field is required.")
        return trimmed


class AuthUserResponse(BaseModel):
    user: UserOut
