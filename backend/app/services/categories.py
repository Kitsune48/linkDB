from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import Category
from app.schemas.categories import CategoryEntry, CreateCategoryInput


class CategoriesService:
    def list_categories(self, db: Session) -> list[CategoryEntry]:
        categories = db.scalars(select(Category).order_by(Category.label.asc())).all()
        return [CategoryEntry.model_validate(category) for category in categories]

    def create_category(self, db: Session, input_data: CreateCategoryInput) -> CategoryEntry:
        existing = db.scalar(select(Category).where(Category.slug == input_data.slug))
        if existing is not None:
            raise AppError("CATEGORY_ALREADY_EXISTS", 409, "Category already exists.")

        category = Category(slug=input_data.slug, label=input_data.label)
        db.add(category)
        db.commit()
        db.refresh(category)
        return CategoryEntry.model_validate(category)


categories_service = CategoriesService()
