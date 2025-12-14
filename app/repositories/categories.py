from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import Category

from .base import CategoryRepository


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, name: str, color: str = "#6366f1") -> Category:
        category = Category(user_id=user_id, name=name, color=color)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def get(self, category_id: int) -> Optional[Category]:
        return self.session.query(Category).filter(Category.id == category_id).first()

    def list_by_user(self, user_id: int) -> List[Category]:
        return self.session.query(Category).filter(Category.user_id == user_id).all()

    def exists_name(self, user_id: int, name: str) -> bool:
        return (
            self.session.query(Category)
            .filter(Category.user_id == user_id, Category.name == name)
            .first()
            is not None
        )

    def update(self, category_id: int, name: Optional[str], color: Optional[str]) -> Optional[Category]:
        category = self.get(category_id)
        if not category:
            return None
        if name is not None:
            category.name = name
        if color is not None:
            category.color = color
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(self, category_id: int) -> bool:
        category = self.get(category_id)
        if not category:
            return False
        self.session.delete(category)
        self.session.commit()
        return True
