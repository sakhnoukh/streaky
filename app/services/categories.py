from typing import Optional, List

from app.models import Category
from app.repositories.base import CategoryRepository, HabitRepository


class CategoryService:
    def __init__(self, categories: CategoryRepository, habits: HabitRepository):
        self.categories = categories
        self.habits = habits

    def create(self, user_id: int, name: str, color: str = "#6366f1") -> Category:
        if self.categories.exists_name(user_id, name):
            raise ValueError("name_exists")
        return self.categories.create(user_id, name, color)

    def get(self, category_id: int, user_id: int) -> Optional[Category]:
        category = self.categories.get(category_id)
        if category and category.user_id != user_id:
            return None
        return category

    def list_by_user(self, user_id: int) -> List[Category]:
        return self.categories.list_by_user(user_id)

    def update(self, category_id: int, user_id: int, name: Optional[str], color: Optional[str]) -> Optional[Category]:
        category = self.categories.get(category_id)
        if not category:
            raise LookupError("not_found")
        if category.user_id != user_id:
            raise LookupError("not_found")
        # Check for duplicate name if name is being changed
        if name and name != category.name and self.categories.exists_name(user_id, name):
            raise ValueError("name_exists")
        return self.categories.update(category_id, name, color)

    def delete(self, category_id: int, user_id: int) -> bool:
        category = self.categories.get(category_id)
        if not category:
            raise LookupError("not_found")
        if category.user_id != user_id:
            raise LookupError("not_found")
        return self.categories.delete(category_id)

    def add_habit_to_category(self, habit_id: int, category_id: int, user_id: int):
        category = self.categories.get(category_id)
        if not category or category.user_id != user_id:
            raise LookupError("category_not_found")
        habit = self.habits.get(habit_id)
        if not habit or habit.user_id != user_id:
            raise LookupError("habit_not_found")
        return self.habits.add_category(habit_id, category)

    def remove_habit_from_category(self, habit_id: int, category_id: int, user_id: int):
        category = self.categories.get(category_id)
        if not category or category.user_id != user_id:
            raise LookupError("category_not_found")
        habit = self.habits.get(habit_id)
        if not habit or habit.user_id != user_id:
            raise LookupError("habit_not_found")
        return self.habits.remove_category(habit_id, category)
