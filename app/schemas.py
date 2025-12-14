from datetime import date
from typing import Optional, List

from pydantic import BaseModel


# Category schemas
class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class CategoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    color: str


class CategoryBrief(BaseModel):
    id: int
    name: str
    color: str


# Habit schemas
class HabitCreate(BaseModel):
    name: str
    goal_type: str
    category_ids: Optional[List[int]] = None


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    goal_type: Optional[str] = None
    category_ids: Optional[List[int]] = None


class HabitLog(BaseModel):
    date: date


class HabitOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    goal_type: str
    categories: List[CategoryBrief] = []


class HabitWithStreak(BaseModel):
    id: int
    name: str
    goal_type: str
    streak: int
    best_streak: int
    categories: List[CategoryBrief] = []

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
