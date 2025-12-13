from datetime import date, time
from typing import Optional, List

from pydantic import BaseModel


class HabitCreate(BaseModel):
    name: str
    goal_type: str
    reminder_time: Optional[time] = None


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    goal_type: Optional[str] = None
    reminder_time: Optional[time] = None


class HabitLog(BaseModel):
    date: date
    journal: Optional[str] = None


class HabitOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    goal_type: str
    reminder_time: Optional[time] = None

class HabitWithStreak(BaseModel):
    id: int
    name: str
    goal_type: str
    streak: int
    best_streak: int
    reminder_time: Optional[time] = None

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

class EntryOut(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    habit_id: int
    date: date
    journal: Optional[str] = None

class EntryUpdate(BaseModel):
    journal: Optional[str] = None
