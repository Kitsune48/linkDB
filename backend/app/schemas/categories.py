from pydantic import BaseModel, Field, field_validator

from app.schemas.common import CamelModel


def validate_category_slug(value: str) -> str:
    trimmed = value.strip().lower()
    if not trimmed:
        raise ValueError("This field is required.")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
    if any(char not in allowed for char in trimmed):
        raise ValueError(
            "Category slug may contain only lowercase letters, numbers and hyphens."
        )
    if trimmed.startswith("-") or trimmed.endswith("-") or "--" in trimmed:
        raise ValueError("Category slug format is invalid.")
    return trimmed


class CategoryEntry(CamelModel):
    slug: str
    label: str


class CreateCategoryInput(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=128)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        return validate_category_slug(value)

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("This field is required.")
        return trimmed
