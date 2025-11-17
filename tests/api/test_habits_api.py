"""API tests for habit endpoints using TestClient."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base
from app.routers.habits import get_db
from datetime import date


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_client():
    """Create test client with clean database for each test."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(test_client):
    """Get authentication token for tests."""
    response = test_client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, test_client):
        """Should return healthy status."""
        response = test_client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, test_client):
        """Should return API information."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data


class TestCreateHabit:
    """Tests for POST /habits endpoint."""

    def test_create_habit_success(self, test_client, auth_headers):
        """Should create a habit successfully."""
        response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Exercise"
        assert data["goal_type"] == "daily"
        assert "id" in data

    def test_create_habit_duplicate_name(self, test_client, auth_headers):
        """Should return 409 when habit name already exists."""
        test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        
        response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_habit_requires_auth(self, test_client):
        """Should require authentication."""
        response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"}
        )
        assert response.status_code == 401

    def test_create_habit_weekly_goal(self, test_client, auth_headers):
        """Should create habit with weekly goal."""
        response = test_client.post(
            "/habits",
            json={"name": "Weekly Task", "goal_type": "weekly"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["goal_type"] == "weekly"

    def test_create_habit_validation_error(self, test_client, auth_headers):
        """Should validate request body."""
        response = test_client.post(
            "/habits",
            json={"name": ""},  # Empty name
            headers=auth_headers
        )
        assert response.status_code == 422


class TestListHabits:
    """Tests for GET /habits endpoint."""

    def test_list_empty_habits(self, test_client, auth_headers):
        """Should return empty list when no habits exist."""
        response = test_client.get("/habits", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_habits_with_streaks(self, test_client, auth_headers):
        """Should list habits with current streak."""
        # Create a habit
        create_response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        habit_id = create_response.json()["id"]
        
        # Log an entry
        test_client.post(
            f"/habits/{habit_id}/entries",
            json={"date": date.today().isoformat()},
            headers=auth_headers
        )
        
        # List habits
        response = test_client.get("/habits", headers=auth_headers)
        assert response.status_code == 200
        habits = response.json()
        assert len(habits) == 1
        assert habits[0]["name"] == "Exercise"
        assert habits[0]["streak"] == 1

    def test_list_habits_requires_auth(self, test_client):
        """Should require authentication."""
        response = test_client.get("/habits")
        assert response.status_code == 401


class TestLogEntry:
    """Tests for POST /habits/{id}/entries endpoint."""

    def test_log_entry_success(self, test_client, auth_headers):
        """Should log an entry successfully."""
        # Create a habit
        create_response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        habit_id = create_response.json()["id"]
        
        # Log entry
        response = test_client.post(
            f"/habits/{habit_id}/entries",
            json={"date": date.today().isoformat()},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True

    def test_log_entry_idempotent(self, test_client, auth_headers):
        """Should be idempotent - logging same day twice succeeds."""
        # Create a habit
        create_response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        habit_id = create_response.json()["id"]
        today = date.today().isoformat()
        
        # Log entry twice
        response1 = test_client.post(
            f"/habits/{habit_id}/entries",
            json={"date": today},
            headers=auth_headers
        )
        response2 = test_client.post(
            f"/habits/{habit_id}/entries",
            json={"date": today},
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_log_entry_nonexistent_habit(self, test_client, auth_headers):
        """Should return 404 when habit does not exist."""
        response = test_client.post(
            "/habits/999/entries",
            json={"date": date.today().isoformat()},
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_log_entry_requires_auth(self, test_client):
        """Should require authentication."""
        response = test_client.post(
            "/habits/1/entries",
            json={"date": date.today().isoformat()}
        )
        assert response.status_code == 401


class TestGetStats:
    """Tests for GET /habits/{id}/stats endpoint."""

    def test_get_stats_7d(self, test_client, auth_headers):
        """Should return 7-day statistics."""
        # Create a habit
        create_response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        habit_id = create_response.json()["id"]
        
        # Get stats
        response = test_client.get(
            f"/habits/{habit_id}/stats?range=7d",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["habit_id"] == habit_id
        assert "current_streak" in data
        assert "best_streak" in data
        assert len(data["days"]) == 7

    def test_get_stats_30d(self, test_client, auth_headers):
        """Should return 30-day statistics."""
        # Create a habit
        create_response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        habit_id = create_response.json()["id"]
        
        # Get stats
        response = test_client.get(
            f"/habits/{habit_id}/stats?range=30d",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["days"]) == 30

    def test_get_stats_nonexistent_habit(self, test_client, auth_headers):
        """Should return 404 when habit does not exist."""
        response = test_client.get(
            "/habits/999/stats?range=7d",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_get_stats_with_entries(self, test_client, auth_headers):
        """Should include entry data in statistics."""
        # Create a habit
        create_response = test_client.post(
            "/habits",
            json={"name": "Exercise", "goal_type": "daily"},
            headers=auth_headers
        )
        habit_id = create_response.json()["id"]
        
        # Log entry for today
        test_client.post(
            f"/habits/{habit_id}/entries",
            json={"date": date.today().isoformat()},
            headers=auth_headers
        )
        
        # Get stats
        response = test_client.get(
            f"/habits/{habit_id}/stats?range=7d",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_streak"] == 1
        # Check that today is marked as done
        today_entry = [d for d in data["days"] if d["date"] == date.today().isoformat()]
        assert len(today_entry) == 1
        assert today_entry[0]["done"] is True

    def test_get_stats_requires_auth(self, test_client):
        """Should require authentication."""
        response = test_client.get("/habits/1/stats?range=7d")
        assert response.status_code == 401
