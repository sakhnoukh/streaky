from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.dependencies import get_current_user
from app.repositories.entries import SqlAlchemyEntryRepository
from app.repositories.habits import SqlAlchemyHabitRepository
from app.schemas import HabitCreate, HabitUpdate, HabitLog, HabitOut, HabitWithStreak, StatsOut, CalendarOut, EntryOut, EntryUpdate
from app.services.habits import HabitService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_habit_service(db: Session = Depends(get_db)) -> HabitService:
    habits_repo = SqlAlchemyHabitRepository(db)
    entries_repo = SqlAlchemyEntryRepository(db)
    return HabitService(habits_repo, entries_repo)

@router.post("/habits", response_model=HabitOut)
def create_habit(
    habit: HabitCreate,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    try:
        # Validate goal_type
        if habit.goal_type not in ["daily", "weekly"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid goal_type. Must be 'daily' or 'weekly'",
            )
        created_habit = service.create(current_user, habit.name, habit.goal_type, habit.reminder_time)  # type: ignore
        return created_habit
    except ValueError as e:
        if str(e) == "name_exists":
            raise HTTPException(
                status_code=409, detail="Habit name already exists"
            ) from e
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/habits", response_model=List[HabitWithStreak])
def list_habits(
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    return service.list_with_streaks(current_user, date.today())

@router.post("/habits/{habit_id}/entries")
def log_entry(
    habit_id: int,
    entry: HabitLog,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    try:
        service.log_today(habit_id, entry.date, entry.journal)
        return {"ok": True}
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e

@router.get("/habits/{habit_id}/stats", response_model=StatsOut)
def get_stats(
    habit_id: int,
    range: str,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    days = 7 if range == "7d" else 30
    try:
        return service.stats(habit_id, days, date.today())
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e

@router.put("/habits/{habit_id}", response_model=HabitOut)
def update_habit(
    habit_id: int,
    habit: HabitUpdate,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    try:
        # Validate goal_type if provided
        if habit.goal_type and habit.goal_type not in ["daily", "weekly"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid goal_type. Must be 'daily' or 'weekly'",
            )
        # Use model_dump(exclude_unset=True) to only get fields that were explicitly set
        habit_dict = habit.model_dump(exclude_unset=True)
        # Only pass reminder_time if it was explicitly in the request
        if 'reminder_time' in habit_dict:
            reminder_time = habit_dict['reminder_time']
        else:
            # Use a sentinel to indicate reminder_time was not provided
            from app.services.habits import _REMINDER_TIME_SENTINEL
            reminder_time = _REMINDER_TIME_SENTINEL
        updated_habit = service.update(habit_id, habit_dict.get('name'), habit_dict.get('goal_type'), reminder_time)
        if not updated_habit:
            raise HTTPException(status_code=404, detail="Habit not found")
        return updated_habit
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e

@router.delete("/habits/{habit_id}")
def delete_habit(
    habit_id: int,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    try:
        service.delete(habit_id)
        return {"ok": True}
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e

@router.get("/habits/{habit_id}/calendar", response_model=CalendarOut)
def get_calendar(
    habit_id: int,
    year: int,
    month: int,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    """
    Get calendar view for a habit showing completion status for each day in a month.
    
    Args:
        habit_id: The ID of the habit
        year: Year (e.g., 2024)
        month: Month (1-12)
    """
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    try:
        return service.calendar(habit_id, current_user, year, month)
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e

@router.get("/habits/{habit_id}/entries/{entry_date}", response_model=EntryOut)
def get_entry(
    habit_id: int,
    entry_date: date,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    """
    Get an entry for a specific habit and date, including journal.
    
    Args:
        habit_id: The ID of the habit
        entry_date: The date of the entry (YYYY-MM-DD)
    """
    try:
        entry = service.get_entry(habit_id, entry_date)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e

@router.put("/habits/{habit_id}/entries/{entry_date}/journal", response_model=EntryOut)
def update_entry_journal(
    habit_id: int,
    entry_date: date,
    entry_update: EntryUpdate,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    """
    Update the journal for a specific entry.
    
    Args:
        habit_id: The ID of the habit
        entry_date: The date of the entry (YYYY-MM-DD)
        entry_update: The journal update data
    """
    try:
        entry = service.update_entry_journal(habit_id, entry_date, entry_update.journal)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e

@router.get("/habits/{habit_id}/entries", response_model=List[EntryOut])
def list_entries(
    habit_id: int,
    service: HabitService = Depends(get_habit_service),
    current_user: int = Depends(get_current_user),
):
    """
    Get all entries for a habit, including journals, ordered by date (newest first).
    
    Args:
        habit_id: The ID of the habit
    """
    try:
        entries = service.list_entries(habit_id)
        return entries
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Habit not found") from e
