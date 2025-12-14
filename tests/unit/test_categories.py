import pytest
from unittest.mock import MagicMock, PropertyMock
from app.services.categories import CategoryService


class TestCategoryService:
    def setup_method(self):
        self.mock_categories_repo = MagicMock()
        self.mock_habits_repo = MagicMock()
        self.service = CategoryService(self.mock_categories_repo, self.mock_habits_repo)

    def test_create_category_success(self):
        self.mock_categories_repo.exists_name.return_value = False
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "Health"
        mock_category.color = "#22c55e"
        mock_category.user_id = 1
        self.mock_categories_repo.create.return_value = mock_category

        result = self.service.create(user_id=1, name="Health", color="#22c55e")

        self.mock_categories_repo.exists_name.assert_called_once_with(1, "Health")
        self.mock_categories_repo.create.assert_called_once_with(1, "Health", "#22c55e")
        assert result.name == "Health"

    def test_create_category_duplicate_name_raises(self):
        self.mock_categories_repo.exists_name.return_value = True

        with pytest.raises(ValueError) as exc_info:
            self.service.create(user_id=1, name="Health")

        assert str(exc_info.value) == "name_exists"

    def test_get_category_success(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 1
        self.mock_categories_repo.get.return_value = mock_category

        result = self.service.get(category_id=1, user_id=1)

        assert result == mock_category

    def test_get_category_wrong_user_returns_none(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 2  # Different user
        self.mock_categories_repo.get.return_value = mock_category

        result = self.service.get(category_id=1, user_id=1)

        assert result is None

    def test_list_by_user(self):
        mock_categories = [MagicMock(), MagicMock()]
        self.mock_categories_repo.list_by_user.return_value = mock_categories

        result = self.service.list_by_user(user_id=1)

        self.mock_categories_repo.list_by_user.assert_called_once_with(1)
        assert result == mock_categories

    def test_update_category_success(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 1
        mock_category.name = "Health"
        self.mock_categories_repo.get.return_value = mock_category
        self.mock_categories_repo.exists_name.return_value = False
        self.mock_categories_repo.update.return_value = mock_category

        result = self.service.update(category_id=1, user_id=1, name="Fitness", color="#ef4444")

        self.mock_categories_repo.update.assert_called_once_with(1, "Fitness", "#ef4444")

    def test_update_category_not_found_raises(self):
        self.mock_categories_repo.get.return_value = None

        with pytest.raises(LookupError) as exc_info:
            self.service.update(category_id=1, user_id=1, name="Fitness", color=None)

        assert str(exc_info.value) == "not_found"

    def test_update_category_wrong_user_raises(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 2  # Different user
        self.mock_categories_repo.get.return_value = mock_category

        with pytest.raises(LookupError) as exc_info:
            self.service.update(category_id=1, user_id=1, name="Fitness", color=None)

        assert str(exc_info.value) == "not_found"

    def test_delete_category_success(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 1
        self.mock_categories_repo.get.return_value = mock_category
        self.mock_categories_repo.delete.return_value = True

        result = self.service.delete(category_id=1, user_id=1)

        self.mock_categories_repo.delete.assert_called_once_with(1)
        assert result is True

    def test_delete_category_not_found_raises(self):
        self.mock_categories_repo.get.return_value = None

        with pytest.raises(LookupError) as exc_info:
            self.service.delete(category_id=1, user_id=1)

        assert str(exc_info.value) == "not_found"

    def test_add_habit_to_category_success(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 1
        self.mock_categories_repo.get.return_value = mock_category

        mock_habit = MagicMock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        self.mock_habits_repo.get.return_value = mock_habit
        self.mock_habits_repo.add_category.return_value = mock_habit

        result = self.service.add_habit_to_category(habit_id=1, category_id=1, user_id=1)

        self.mock_habits_repo.add_category.assert_called_once_with(1, mock_category)

    def test_add_habit_to_category_category_not_found(self):
        self.mock_categories_repo.get.return_value = None

        with pytest.raises(LookupError) as exc_info:
            self.service.add_habit_to_category(habit_id=1, category_id=1, user_id=1)

        assert str(exc_info.value) == "category_not_found"

    def test_add_habit_to_category_habit_not_found(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 1
        self.mock_categories_repo.get.return_value = mock_category
        self.mock_habits_repo.get.return_value = None

        with pytest.raises(LookupError) as exc_info:
            self.service.add_habit_to_category(habit_id=1, category_id=1, user_id=1)

        assert str(exc_info.value) == "habit_not_found"

    def test_remove_habit_from_category_success(self):
        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.user_id = 1
        self.mock_categories_repo.get.return_value = mock_category

        mock_habit = MagicMock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        self.mock_habits_repo.get.return_value = mock_habit
        self.mock_habits_repo.remove_category.return_value = mock_habit

        result = self.service.remove_habit_from_category(habit_id=1, category_id=1, user_id=1)

        self.mock_habits_repo.remove_category.assert_called_once_with(1, mock_category)
