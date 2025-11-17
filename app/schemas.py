from datetime import date

from pydantic import BaseModel


class HabitCreate(BaseModel):
    name: str
    goal_type: str


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

class StatsOut(BaseModel):
    habit_id: int
    current_streak: int
    best_streak: int
    days: list[dict]
