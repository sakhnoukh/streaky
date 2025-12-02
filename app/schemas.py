from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class HabitCreate(BaseModel):
    name: str
    goal_type: str


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    goal_type: Optional[str] = None


class HabitLog(BaseModel):
    date: date


class HabitOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    goal_type: str

class HabitWithStreak(BaseModel):
    id: int
    name: str
    goal_type: str
    streak: int
    best_streak: int

class StatsOut(BaseModel):
    habit_id: int
    current_streak: int
    best_streak: int
    days: List[dict]

class CalendarDay(BaseModel):
    date: str
    completed: bool

class CalendarOut(BaseModel):
    habit_id: int
    year: int
    month: int
    days: List[CalendarDay]
