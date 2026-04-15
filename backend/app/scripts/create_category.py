import sys

from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal
from app.scripts.common import print_database_connection_error
from app.schemas.categories import CreateCategoryInput
from app.services.categories import categories_service


def main() -> int:
    load_dotenv()
    if len(sys.argv) != 3:
        print("Usage: python -m app.scripts.create_category <slug> <label>", file=sys.stderr)
        return 1

    _, slug, label = sys.argv
    session = SessionLocal()
    try:
        category = categories_service.create_category(
            session,
            CreateCategoryInput(slug=slug, label=label),
        )
        print("Category created successfully.")
        print(f"slug: {category.slug}")
        print(f"label: {category.label}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OperationalError as error:
        raise SystemExit(print_database_connection_error("create category", error))
