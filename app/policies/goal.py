from datetime import date, timedelta
from typing import Protocol


class GoalPolicy(Protocol):
    def window(self, days: int, today: date) -> tuple[date, date]: ...
    def is_hit(self, dates: set[date], d: date) -> bool: ...

class DailyPolicy:
    def window(self, days: int, today: date): return today - timedelta(days=days-1), today
    def is_hit(self, dates: set[date], d: date): return d in dates

class WeeklyPolicy:
    def window(self, days: int, today: date):
        return today - timedelta(days=days - 1), today

    def is_hit(self, dates: set[date], d: date):
        # MVP placeholder: any day of week counts
        return d.isoweekday() in {1, 2, 3, 4, 5, 6, 7} and d in dates
