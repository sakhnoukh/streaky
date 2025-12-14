import pytest
import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


client = TestClient(app)


def unique_name(prefix: str) -> str:
    """Generate a unique name for test isolation."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def get_auth_headers():
    """Get authentication headers for testing."""
    username = unique_name("testcatuser")
    response = client.post(
        "/auth/register",
        json={"username": username, "password": "testpass123"}
    )
    response = client.post(
        "/token",
        data={"username": username, "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCategoriesAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.headers = get_auth_headers()

    def test_create_category(self):
        name = unique_name("Health")
        response = client.post(
            "/categories",
            json={"name": name, "color": "#22c55e"},
            headers=self.headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert data["color"] == "#22c55e"
        assert "id" in data

    def test_create_category_duplicate_name(self):
        name = unique_name("DuplicateTest")
        # Create first category
        client.post(
            "/categories",
            json={"name": name, "color": "#22c55e"},
            headers=self.headers
        )
        # Try to create duplicate
        response = client.post(
            "/categories",
            json={"name": name, "color": "#ef4444"},
            headers=self.headers
        )
        assert response.status_code == 409

    def test_list_categories(self):
        name = unique_name("ListTest")
        # Create a category first
        client.post(
            "/categories",
            json={"name": name, "color": "#6366f1"},
            headers=self.headers
        )
        
        response = client.get("/categories", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least one category
        assert len(data) >= 1

    def test_get_category(self):
        name = unique_name("GetTest")
        # Create a category
        create_response = client.post(
            "/categories",
            json={"name": name, "color": "#8b5cf6"},
            headers=self.headers
        )
        category_id = create_response.json()["id"]

        response = client.get(f"/categories/{category_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == name
        assert data["color"] == "#8b5cf6"

    def test_get_category_not_found(self):
        response = client.get("/categories/99999", headers=self.headers)
        assert response.status_code == 404

    def test_update_category(self):
        name = unique_name("UpdateTest")
        updated_name = unique_name("UpdatedName")
        # Create a category
        create_response = client.post(
            "/categories",
            json={"name": name, "color": "#22c55e"},
            headers=self.headers
        )
        category_id = create_response.json()["id"]

        response = client.put(
            f"/categories/{category_id}",
            json={"name": updated_name, "color": "#ef4444"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == updated_name
        assert data["color"] == "#ef4444"

    def test_delete_category(self):
        name = unique_name("DeleteTest")
        # Create a category
        create_response = client.post(
            "/categories",
            json={"name": name, "color": "#22c55e"},
            headers=self.headers
        )
        category_id = create_response.json()["id"]

        response = client.delete(f"/categories/{category_id}", headers=self.headers)
        assert response.status_code == 200
        assert response.json()["ok"] is True

        # Verify it's deleted
        get_response = client.get(f"/categories/{category_id}", headers=self.headers)
        assert get_response.status_code == 404

    def test_add_habit_to_category(self):
        cat_name = unique_name("HabitCatTest")
        habit_name = unique_name("CatTestHabit")
        # Create a category
        cat_response = client.post(
            "/categories",
            json={"name": cat_name, "color": "#22c55e"},
            headers=self.headers
        )
        category_id = cat_response.json()["id"]

        # Create a habit
        habit_response = client.post(
            "/habits",
            json={"name": habit_name, "goal_type": "daily"},
            headers=self.headers
        )
        habit_id = habit_response.json()["id"]

        # Add habit to category
        response = client.post(
            f"/categories/{category_id}/habits/{habit_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True

    def test_remove_habit_from_category(self):
        cat_name = unique_name("RemoveHabitTest")
        habit_name = unique_name("RemoveTestHabit")
        # Create a category
        cat_response = client.post(
            "/categories",
            json={"name": cat_name, "color": "#22c55e"},
            headers=self.headers
        )
        category_id = cat_response.json()["id"]

        # Create a habit
        habit_response = client.post(
            "/habits",
            json={"name": habit_name, "goal_type": "daily"},
            headers=self.headers
        )
        habit_id = habit_response.json()["id"]

        # Add habit to category first
        client.post(
            f"/categories/{category_id}/habits/{habit_id}",
            headers=self.headers
        )

        # Remove habit from category
        response = client.delete(
            f"/categories/{category_id}/habits/{habit_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True

    def test_filter_habits_by_category(self):
        cat_name = unique_name("FilterTest")
        habit1_name = unique_name("FilterHabit1")
        habit2_name = unique_name("FilterHabit2")
        # Create a category
        cat_response = client.post(
            "/categories",
            json={"name": cat_name, "color": "#22c55e"},
            headers=self.headers
        )
        category_id = cat_response.json()["id"]

        # Create habits
        habit1_response = client.post(
            "/habits",
            json={"name": habit1_name, "goal_type": "daily"},
            headers=self.headers
        )
        habit1_id = habit1_response.json()["id"]

        client.post(
            "/habits",
            json={"name": habit2_name, "goal_type": "daily"},
            headers=self.headers
        )

        # Add only habit1 to category
        client.post(
            f"/categories/{category_id}/habits/{habit1_id}",
            headers=self.headers
        )

        # Filter habits by category
        response = client.get(
            f"/habits?category_id={category_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should only return habits in this category
        habit_names = [h["name"] for h in data]
        assert habit1_name in habit_names

    def test_unauthorized_access(self):
        response = client.get("/categories")
        assert response.status_code == 401

        response = client.post("/categories", json={"name": "Test", "color": "#000"})
        assert response.status_code == 401
