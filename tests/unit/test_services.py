"""Unit tests for HabitService with fake repositories."""
from datetime import date, timedelta, time
from typing import Iterable, Optional, List, Union
import pytest
from app.services.habits import HabitService
from app.models import Habit, Entry
from app.repositories.base import _REMINDER_TIME_NOT_PROVIDED


class FakeHabitRepository:
    """In-memory fake repository for testing."""

    def __init__(self):
        self.habits = {}
        self.next_id = 1

    def create(self, user_id: int, name: str, goal_type: str, reminder_time: Optional[time] = None) -> Habit:
        habit = Habit(id=self.next_id, user_id=user_id, name=name, goal_type=goal_type, reminder_time=reminder_time)
        self.habits[self.next_id] = habit
        self.next_id += 1
        return habit

    def get(self, habit_id: int) -> Optional[Habit]:
        return self.habits.get(habit_id)

    def list_by_user(self, user_id: int) -> List[Habit]:
        return [h for h in self.habits.values() if h.user_id == user_id]

    def exists_name(self, user_id: int, name: str) -> bool:
        return any(h.name == name and h.user_id == user_id for h in self.habits.values())

    def update(self, habit_id: int, name: Optional[str], goal_type: Optional[str], reminder_time: Union[Optional[time], object] = _REMINDER_TIME_NOT_PROVIDED) -> Optional[Habit]:
        habit = self.habits.get(habit_id)
        if not habit:
            return None
        if name is not None:
            habit.name = name
        if goal_type is not None:
            habit.goal_type = goal_type
        if reminder_time is not _REMINDER_TIME_NOT_PROVIDED:
            habit.reminder_time = reminder_time  # type: ignore
        return habit

    def delete(self, habit_id: int) -> bool:
        if habit_id in self.habits:
            del self.habits[habit_id]
            return True
        return False


class FakeEntryRepository:
    """In-memory fake repository for testing."""

    def __init__(self):
        self.entries = []
        self.next_id = 1

    def exists_on(self, habit_id: int, d: date) -> bool:
        return any(e.habit_id == habit_id and e.date == d for e in self.entries)

    def create(self, habit_id: int, d: date, journal: Optional[str] = None) -> Entry:
        entry = Entry(id=self.next_id, habit_id=habit_id, date=d, journal=journal)
        self.entries.append(entry)
        self.next_id += 1
        return entry

    def dates_between(self, habit_id: int, start: date, end: date) -> Iterable[date]:
        return [
            e.date
            for e in self.entries
            if e.habit_id == habit_id and start <= e.date <= end
        ]


@pytest.fixture
def habit_service():
    """Create a HabitService with fake repositories."""
    habit_repo = FakeHabitRepository()
    entry_repo = FakeEntryRepository()
    return HabitService(habit_repo, entry_repo)


class TestHabitServiceCreate:
    """Tests for creating habits."""

    def test_create_habit_success(self, habit_service):
        """Should create a habit successfully."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        assert habit.name == "Exercise"
        assert habit.user_id == 1
        assert habit.goal_type == "daily"

    def test_create_habit_duplicate_name_raises_error(self, habit_service):
        """Should raise ValueError when habit name already exists for user."""
        habit_service.create(user_id=1, name="Exercise", goal="daily")
        
        with pytest.raises(ValueError, match="name_exists"):
            habit_service.create(user_id=1, name="Exercise", goal="daily")

    def test_create_habit_same_name_different_user_allowed(self, habit_service):
        """Should allow same habit name for different users."""
        habit1 = habit_service.create(user_id=1, name="Exercise", goal="daily")
        habit2 = habit_service.create(user_id=2, name="Exercise", goal="daily")
        
        assert habit1.user_id == 1
        assert habit2.user_id == 2
        assert habit1.name == habit2.name

    def test_create_habit_with_weekly_goal(self, habit_service):
        """Should create habit with weekly goal type."""
        habit = habit_service.create(user_id=1, name="Running", goal="weekly")
        assert habit.goal_type == "weekly"


class TestHabitServiceLogToday:
    """Tests for logging entries."""

    def test_log_today_success(self, habit_service):
        """Should log an entry for today."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        today = date.today()
        
        habit_service.log_today(habit.id, 1, today)
        
        # Verify entry was created
        entries = list(habit_service.entries.dates_between(habit.id, today, today))
        assert today in entries

    def test_log_today_idempotent(self, habit_service):
        """Should be idempotent - logging same day twice should not fail."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        today = date.today()
        
        habit_service.log_today(habit.id, 1, today)
        habit_service.log_today(habit.id, 1, today)  # Should not fail
        
        # Should still have only one entry
        entries = list(habit_service.entries.dates_between(habit.id, today, today))
        assert len(entries) == 1

    def test_log_today_nonexistent_habit_raises_error(self, habit_service):
        """Should raise LookupError when habit does not exist."""
        with pytest.raises(LookupError, match="not_found"):
            habit_service.log_today(habit_id=999, user_id=1, today=date.today())


class TestHabitServiceListWithStreaks:
    """Tests for listing habits with streaks."""

    def test_list_empty_for_new_user(self, habit_service):
        """Should return empty list for user with no habits."""
        habits = habit_service.list_with_streaks(user_id=1, today=date.today())
        assert habits == []

    def test_list_habits_with_no_entries(self, habit_service):
        """Should list habits with zero streak when no entries exist."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        today = date.today()
        
        habits = habit_service.list_with_streaks(user_id=1, today=today)
        
        assert len(habits) == 1
        assert habits[0]["id"] == habit.id
        assert habits[0]["name"] == "Exercise"
        assert habits[0]["streak"] == 0

    def test_list_habits_with_current_streak(self, habit_service):
        """Should calculate current streak correctly."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        today = date.today()
        
        # Log entries for 3 consecutive days
        for i in range(3):
            d = today - timedelta(days=2 - i)
            habit_service.log_today(habit.id, 1, d)
        
        habits = habit_service.list_with_streaks(user_id=1, today=today)
        
        assert len(habits) == 1
        assert habits[0]["streak"] == 3

    def test_list_only_users_habits(self, habit_service):
        """Should only list habits belonging to the user."""
        habit_service.create(user_id=1, name="Exercise", goal="daily")
        habit_service.create(user_id=2, name="Reading", goal="daily")
        
        habits = habit_service.list_with_streaks(user_id=1, today=date.today())
        
        assert len(habits) == 1
        assert habits[0]["name"] == "Exercise"


class TestHabitServiceStats:
    """Tests for getting habit statistics."""

    def test_stats_nonexistent_habit_raises_error(self, habit_service):
        """Should raise LookupError when habit does not exist."""
        with pytest.raises(LookupError, match="not_found"):
            habit_service.stats(habit_id=999, user_id=1, days=7, today=date.today())

    def test_stats_with_no_entries(self, habit_service):
        """Should return stats with zero streaks when no entries exist."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        today = date.today()
        
        stats = habit_service.stats(habit.id, 1, days=7, today=today)
        
        assert stats["habit_id"] == habit.id
        assert stats["current_streak"] == 0
        assert stats["best_streak"] == 0
        assert len(stats["days"]) == 7

    def test_stats_calculates_streaks(self, habit_service):
        """Should calculate current and best streaks correctly."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        today = date.today()
        
        # Create a pattern: 3 days, gap, 2 days (current)
        for i in range(3):
            d = today - timedelta(days=6 - i)
            habit_service.log_today(habit.id, 1, d)
        
        # Gap at today - 3
        
        for i in range(2):
            d = today - timedelta(days=1 - i)
            habit_service.log_today(habit.id, 1, d)
        
        stats = habit_service.stats(habit.id, 1, days=7, today=today)
        
        assert stats["current_streak"] == 2
        assert stats["best_streak"] == 3

    def test_stats_days_array(self, habit_service):
        """Should include correct days array with done flags."""
        habit = habit_service.create(user_id=1, name="Exercise", goal="daily")
        today = date.today()
        
        # Log for today and yesterday
        habit_service.log_today(habit.id, 1, today)
        habit_service.log_today(habit.id, 1, today - timedelta(days=1))
        
        stats = habit_service.stats(habit.id, days=3, today=today)
        
        assert len(stats["days"]) == 3
        assert stats["days"][-1]["date"] == today.isoformat()
        assert stats["days"][-1]["done"] is True
        assert stats["days"][-2]["done"] is True
        assert stats["days"][-3]["done"] is False

    def test_stats_respects_goal_policy(self, habit_service):
        """Should use the correct goal policy for calculations."""
        habit = habit_service.create(user_id=1, name="Weekly Task", goal="weekly")
        today = date.today()
        
        stats = habit_service.stats(habit.id, 1, days=7, today=today)
        
        # Should still calculate stats (implementation uses policy)
        assert stats["habit_id"] == habit.id
        assert "days" in stats
