from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.constants import LinkStatus
from app.schemas.categories import validate_category_slug
from app.schemas.common import CamelModel, MetaPage, SessionUser


class CategoryEntry(CamelModel):
    slug: str
    label: str


class LinkOut(CamelModel):
    id: int
    link: str
    title: str
    description: str
    categories: list[CategoryEntry]
    status: LinkStatus
    added_by_id: int
    created_at: datetime
    updated_at: datetime
    added_by: SessionUser
    is_in_read_later: bool = False


class PaginatedLinksResponse(CamelModel):
    items: list[LinkOut]
    meta: MetaPage


class CreateLinkBody(BaseModel):
    link: str
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    categories: list[str]
    status: LinkStatus

    @field_validator("link")
    @classmethod
    def validate_link(cls, value: str) -> str:
        trimmed = value.strip()
        parsed = urlsplit(trimmed)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Input should be a valid URL.")
        return trimmed

    @field_validator("title", "description")
    @classmethod
    def validate_trimmed_string(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("This field is required.")
        return trimmed

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, value: list[str]) -> list[str]:
        normalized = [validate_category_slug(category) for category in value]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Categories must be unique.")
        return normalized


class UpdateLinkBody(BaseModel):
    link: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    categories: list[str] | None = None
    status: LinkStatus | None = None

    @field_validator("link")
    @classmethod
    def validate_optional_link(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        parsed = urlsplit(trimmed)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Input should be a valid URL.")
        return trimmed

    @field_validator("title", "description")
    @classmethod
    def validate_optional_trimmed_string(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("This field is required.")
        return trimmed

    @field_validator("categories")
    @classmethod
    def validate_optional_categories(
        cls,
        value: list[str] | None,
    ) -> list[str] | None:
        if value is None:
            return None
        normalized = [validate_category_slug(category) for category in value]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Categories must be unique.")
        return normalized

    @model_validator(mode="after")
    def ensure_at_least_one_field(self) -> "UpdateLinkBody":
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one field must be provided.")
        return self


class ListLinksQuery(CamelModel):
    q: str | None = None
    category: str | None = None
    categories: list[str] | None = None
    status: LinkStatus | None = None
    added_by: int | None = None
    page: int = 1
    limit: int = 20
    sort: str = "updatedAt"
    order: str = "desc"

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_category_slug(value)

    @field_validator("categories")
    @classmethod
    def validate_categories_list(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        normalized = [validate_category_slug(category) for category in value]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Categories must be unique.")
        return normalized

    @field_validator("q")
    @classmethod
    def validate_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @field_validator("added_by")
    @classmethod
    def validate_added_by(cls, value: int | None) -> int | None:
        if value is None or value > 0:
            return value
        raise ValueError("Input should be greater than 0.")

    @field_validator("page", "limit")
    @classmethod
    def validate_positive_int(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Input should be greater than 0.")
        return value

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, value: int) -> int:
        if value > 100:
            raise ValueError("Input should be less than or equal to 100.")
        return value

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, value: str) -> str:
        if value not in {"createdAt", "updatedAt", "title"}:
            raise ValueError("Invalid sort field.")
        return value

    @field_validator("order")
    @classmethod
    def validate_order(cls, value: str) -> str:
        if value not in {"asc", "desc"}:
            raise ValueError("Invalid order field.")
        return value

    def selected_categories(self) -> list[str]:
        if self.categories:
            return self.categories
        return [self.category] if self.category else []
