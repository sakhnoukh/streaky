from collections.abc import Iterable
from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models import Entry

from .base import EntryRepository


class SqlAlchemyEntryRepository(EntryRepository):
    def __init__(self, session: Session):
        self.session = session

    def exists_on(self, habit_id: int, d: date) -> bool:
        return (
            self.session.query(Entry)
            .filter(Entry.habit_id == habit_id, Entry.date == d)
            .first()
            is not None
        )

    def create(self, habit_id: int, d: date, journal: Optional[str] = None) -> Entry:
        entry = Entry(habit_id=habit_id, date=d, journal=journal)
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def dates_between(self, habit_id: int, start: date, end: date) -> Iterable[date]:
        entries = self.session.query(Entry.date).filter(
            Entry.habit_id == habit_id,
            Entry.date >= start,
            Entry.date <= end
        ).all()
        return [entry.date for entry in entries]

    def get_by_date(self, habit_id: int, d: date) -> Optional[Entry]:
        return (
            self.session.query(Entry)
            .filter(Entry.habit_id == habit_id, Entry.date == d)
            .first()
        )

    def update_journal(self, habit_id: int, d: date, journal: Optional[str]) -> Optional[Entry]:
        entry = self.get_by_date(habit_id, d)
        if entry:
            entry.journal = journal
            self.session.commit()
            self.session.refresh(entry)
        return entry

    def list_by_habit(self, habit_id: int) -> List[Entry]:
        return (
            self.session.query(Entry)
            .filter(Entry.habit_id == habit_id)
            .order_by(Entry.date.desc())
            .all()
        )
