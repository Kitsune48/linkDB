from app.domain.constants import DEFAULT_CATEGORIES


def category_rows() -> list[dict[str, str]]:
    return list(DEFAULT_CATEGORIES)
