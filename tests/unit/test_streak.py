"""Unit tests for streak utility functions."""
from datetime import date, timedelta
from app.utils.streak import current_streak, best_streak


class TestCurrentStreak:
    """Tests for current_streak function."""

    def test_no_streak_when_today_not_in_dates(self):
        """Should return 0 when today is not in the dates set."""
        dates = {date(2024, 1, 1), date(2024, 1, 2)}
        today = date(2024, 1, 5)
        assert current_streak(dates, today) == 0

    def test_streak_of_one_when_only_today(self):
        """Should return 1 when only today is logged."""
        today = date(2024, 1, 5)
        dates = {today}
        assert current_streak(dates, today) == 1

    def test_consecutive_streak(self):
        """Should count consecutive days correctly."""
        today = date(2024, 1, 5)
        dates = {
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
            date(2024, 1, 5),
        }
        assert current_streak(dates, today) == 4

    def test_streak_with_gap(self):
        """Should only count from today backwards until first gap."""
        today = date(2024, 1, 5)
        dates = {
            date(2024, 1, 1),
            # Gap on Jan 2
            date(2024, 1, 3),
            date(2024, 1, 4),
            date(2024, 1, 5),
        }
        assert current_streak(dates, today) == 3

    def test_empty_dates(self):
        """Should return 0 for empty dates set."""
        today = date(2024, 1, 5)
        assert current_streak(set(), today) == 0


class TestBestStreak:
    """Tests for best_streak function."""

    def test_empty_dates(self):
        """Should return 0 for empty dates set."""
        assert best_streak(set()) == 0

    def test_single_date(self):
        """Should return 1 for single date."""
        dates = {date(2024, 1, 1)}
        assert best_streak(dates) == 1

    def test_consecutive_dates(self):
        """Should count consecutive dates correctly."""
        dates = {
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
        }
        assert best_streak(dates) == 4

    def test_multiple_streaks_returns_best(self):
        """Should return the longest streak when multiple exist."""
        dates = {
            # First streak: 3 days
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 3),
            # Gap
            # Second streak: 5 days (best)
            date(2024, 1, 10),
            date(2024, 1, 11),
            date(2024, 1, 12),
            date(2024, 1, 13),
            date(2024, 1, 14),
            # Gap
            # Third streak: 2 days
            date(2024, 1, 20),
            date(2024, 1, 21),
        }
        assert best_streak(dates) == 5

    def test_non_consecutive_dates(self):
        """Should handle scattered dates correctly."""
        dates = {
            date(2024, 1, 1),
            date(2024, 1, 3),
            date(2024, 1, 5),
        }
        assert best_streak(dates) == 1

    def test_all_consecutive(self):
        """Should handle a single long streak."""
        dates = {date(2024, 1, 1) + timedelta(days=i) for i in range(30)}
        assert best_streak(dates) == 30
