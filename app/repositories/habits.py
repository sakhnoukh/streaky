from datetime import time
from typing import Optional, List, Union
from sqlalchemy.orm import Session

from app.models import Habit

from .base import HabitRepository, _REMINDER_TIME_NOT_PROVIDED


class SqlAlchemyHabitRepository(HabitRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, name: str, goal_type: str, reminder_time: Optional[time] = None) -> Habit:
        habit = Habit(user_id=user_id, name=name, goal_type=goal_type, reminder_time=reminder_time)
        self.session.add(habit)
        self.session.commit()
        self.session.refresh(habit)
        return habit

    def get(self, habit_id: int) -> Optional[Habit]:
        return self.session.query(Habit).filter(Habit.id == habit_id).first()

    def list_by_user(self, user_id: int) -> List[Habit]:
        return self.session.query(Habit).filter(Habit.user_id == user_id).all()

    def exists_name(self, user_id: int, name: str) -> bool:
        return (
            self.session.query(Habit)
            .filter(Habit.user_id == user_id, Habit.name == name)
            .first()
            is not None
        )

    def update(self, habit_id: int, name: Optional[str], goal_type: Optional[str], reminder_time: Union[Optional[time], object] = _REMINDER_TIME_NOT_PROVIDED) -> Optional[Habit]:
        habit = self.get(habit_id)
        if not habit:
            return None
        if name is not None:
            habit.name = name
        if goal_type is not None:
            habit.goal_type = goal_type
        # Update reminder_time only if it was explicitly provided (not the sentinel)
        # None means clear reminder, any time value means set it
        if reminder_time is not _REMINDER_TIME_NOT_PROVIDED:
            habit.reminder_time = reminder_time  # type: ignore
        self.session.commit()
        self.session.refresh(habit)
        return habit

    def delete(self, habit_id: int) -> bool:
        habit = self.get(habit_id)
        if not habit:
            return False
        self.session.delete(habit)
        self.session.commit()
        return True
