"""Unit tests for goal policy strategies."""
from datetime import date, timedelta
from app.policies.goal import DailyPolicy, WeeklyPolicy


class TestDailyPolicy:
    """Tests for DailyPolicy strategy."""

    def test_window_calculates_correct_range(self):
        """Should calculate the correct date window for given days."""
        policy = DailyPolicy()
        today = date(2024, 1, 15)
        
        # 7 days window
        start, end = policy.window(7, today)
        assert start == date(2024, 1, 9)  # 7 days before including today
        assert end == today
        
        # 30 days window
        start, end = policy.window(30, today)
        assert start == date(2023, 12, 17)  # 30 days before including today
        assert end == today

    def test_window_single_day(self):
        """Should handle single day window."""
        policy = DailyPolicy()
        today = date(2024, 1, 15)
        start, end = policy.window(1, today)
        assert start == today
        assert end == today

    def test_is_hit_when_date_in_set(self):
        """Should return True when date is in the set."""
        policy = DailyPolicy()
        target_date = date(2024, 1, 15)
        dates = {date(2024, 1, 14), target_date, date(2024, 1, 16)}
        assert policy.is_hit(dates, target_date) is True

    def test_is_hit_when_date_not_in_set(self):
        """Should return False when date is not in the set."""
        policy = DailyPolicy()
        target_date = date(2024, 1, 15)
        dates = {date(2024, 1, 14), date(2024, 1, 16)}
        assert policy.is_hit(dates, target_date) is False

    def test_is_hit_empty_set(self):
        """Should return False for empty dates set."""
        policy = DailyPolicy()
        target_date = date(2024, 1, 15)
        assert policy.is_hit(set(), target_date) is False


class TestWeeklyPolicy:
    """Tests for WeeklyPolicy strategy."""

    def test_window_calculates_correct_range(self):
        """Should calculate the correct date window for given days."""
        policy = WeeklyPolicy()
        today = date(2024, 1, 15)
        
        # 7 days window
        start, end = policy.window(7, today)
        assert start == date(2024, 1, 9)
        assert end == today
        
        # 30 days window
        start, end = policy.window(30, today)
        assert start == date(2023, 12, 17)
        assert end == today

    def test_is_hit_when_date_in_set_weekday(self):
        """Should return True when date is in the set for any day of week."""
        policy = WeeklyPolicy()
        # Monday
        target_date = date(2024, 1, 15)  # Monday
        dates = {target_date}
        assert policy.is_hit(dates, target_date) is True
        
        # Sunday
        target_date = date(2024, 1, 14)  # Sunday
        dates = {target_date}
        assert policy.is_hit(dates, target_date) is True

    def test_is_hit_when_date_not_in_set(self):
        """Should return False when date is not in the set."""
        policy = WeeklyPolicy()
        target_date = date(2024, 1, 15)
        dates = {date(2024, 1, 14), date(2024, 1, 16)}
        assert policy.is_hit(dates, target_date) is False
