from collections.abc import Iterable
from datetime import date

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

    def create(self, habit_id: int, d: date) -> Entry:
        entry = Entry(habit_id=habit_id, date=d)
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
