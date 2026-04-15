from datetime import datetime

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,
    )


class MetaPage(CamelModel):
    page: int
    limit: int
    total: int
    total_pages: int


class SessionUser(CamelModel):
    id: int
    username: str


class UserOut(CamelModel):
    id: int
    username: str
    created_at: datetime
    updated_at: datetime
