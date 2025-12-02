from datetime import date, timedelta
from typing import Literal, Optional
from calendar import monthrange

from app.policies.goal import DailyPolicy, GoalPolicy, WeeklyPolicy
from app.repositories.base import EntryRepository, HabitRepository
from app.utils.streak import best_streak, current_streak

Goal = Literal["daily", "weekly"]


def _policy(goal: Goal) -> GoalPolicy:
    return DailyPolicy() if goal == "daily" else WeeklyPolicy()


class HabitService:
    def __init__(self, habits: HabitRepository, entries: EntryRepository):
        self.habits, self.entries = habits, entries

    def create(self, user_id: int, name: str, goal: Goal = "daily"):
        if self.habits.exists_name(user_id, name):
            raise ValueError("name_exists")
        return self.habits.create(user_id, name, goal)

    def log_today(self, habit_id: int, today: date):
        if not self.habits.get(habit_id):
            raise LookupError("not_found")
        if not self.entries.exists_on(habit_id, today):
            self.entries.create(habit_id, today)

    def list_with_streaks(self, user_id: int, today: date):
        out = []
        for h in self.habits.list_by_user(user_id):
            # Fetch last 365 days to calculate current streak
            start = today - timedelta(days=365)
            dates = set(self.entries.dates_between(h.id, start, today))
            out.append({"id": h.id, "name": h.name, "goal_type": h.goal_type,
                        "streak": current_streak(dates, today),
                        "best_streak": best_streak(dates)})
        return out

    def update(self, habit_id: int, name: Optional[str], goal_type: Optional[str]):
        if not self.habits.get(habit_id):
            raise LookupError("not_found")
        return self.habits.update(habit_id, name, goal_type)

    def delete(self, habit_id: int):
        if not self.habits.get(habit_id):
            raise LookupError("not_found")
        return self.habits.delete(habit_id)

    def stats(self, habit_id: int, days: int, today: date):
        h = self.habits.get(habit_id)
        if not h:
            raise LookupError("not_found")
        pol = _policy(h.goal_type)  # type: ignore[arg-type]
        start, end = pol.window(days, today)
        ds = set(self.entries.dates_between(h.id, start, end))
        return {
            "habit_id": h.id,
            "current_streak": current_streak(ds, today),
            "best_streak": best_streak(ds),
            "days": [{"date": d.isoformat(), "done": pol.is_hit(ds, d)}
                     for d in (start + timedelta(n) for n in range((end-start).days+1))]
        }

    def calendar(self, habit_id: int, user_id: int, year: int, month: int):
        h = self.habits.get(habit_id)
        if not h:
            raise LookupError("not_found")
        # Validate that the habit belongs to the user
        if h.user_id != user_id:
            raise LookupError("not_found")
        
        # Get first and last day of the month
        first_day = date(year, month, 1)
        last_day_num = monthrange(year, month)[1]
        last_day = date(year, month, last_day_num)
        
        # Get all entry dates for this habit in the month
        entry_dates = set(self.entries.dates_between(h.id, first_day, last_day))
        
        # Get policy for checking completion
        pol = _policy(h.goal_type)  # type: ignore[arg-type]
        
        # Generate all days in the month
        days = []
        current = first_day
        while current <= last_day:
            days.append({
                "date": current.isoformat(),
                "completed": pol.is_hit(entry_dates, current)
            })
            current += timedelta(days=1)
        
        return {
            "habit_id": h.id,
            "year": year,
            "month": month,
            "days": days
        }
