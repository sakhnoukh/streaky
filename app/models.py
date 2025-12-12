from datetime import date as date_type
from typing import Optional

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)  # Length required for SQL Server index
    hashed_password = Column(String(255))

class Habit(Base):
    __tablename__ = "habits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255), index=True)  # Length required for SQL Server index
    goal_type: Mapped[str] = mapped_column(String(50))  # 'daily' or 'weekly'

    entries = relationship("Entry", back_populates="habit", cascade="all, delete-orphan")

class Entry(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"))
    date: Mapped[date_type] = mapped_column(Date)
    journal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    habit = relationship("Habit", back_populates="entries")
