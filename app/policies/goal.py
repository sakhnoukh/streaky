from datetime import date, timedelta
from typing import Protocol, Tuple, Set


class GoalPolicy(Protocol):
    def window(self, days: int, today: date) -> Tuple[date, date]: ...
    def is_hit(self, dates: Set[date], d: date) -> bool: ...

class DailyPolicy:
    def window(self, days: int, today: date): return today - timedelta(days=days-1), today
    def is_hit(self, dates: Set[date], d: date): return d in dates

class WeeklyPolicy:
    def window(self, days: int, today: date):
        return today - timedelta(days=days - 1), today

    def is_hit(self, dates: Set[date], d: date):
        # MVP placeholder: any day of week counts
        return d.isoweekday() in {1, 2, 3, 4, 5, 6, 7} and d in dates
