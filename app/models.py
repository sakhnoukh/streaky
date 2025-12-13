from datetime import date as date_type, time as time_type
from typing import Optional

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)  # Length required for SQL Server index
    hashed_password = Column(String(255), nullable=False)

class Habit(Base):
    __tablename__ = "habits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)  # Length required for SQL Server index
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'daily' or 'weekly'
    reminder_time: Mapped[Optional[time_type]] = mapped_column(Time, nullable=True)  # Optional reminder time

    entries = relationship("Entry", back_populates="habit", cascade="all, delete-orphan")

class Entry(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    journal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    habit = relationship("Habit", back_populates="entries")
