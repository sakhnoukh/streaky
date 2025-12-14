from datetime import date as date_type

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

# Association table for many-to-many relationship between habits and categories
habit_categories = Table(
    "habit_categories",
    Base.metadata,
    Column("habit_id", Integer, ForeignKey("habits.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)  # Length required for SQL Server index
    hashed_password = Column(String(255))

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100), index=True)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")  # Hex color code

    habits = relationship("Habit", secondary=habit_categories, back_populates="categories")


class Habit(Base):
    __tablename__ = "habits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255), index=True)  # Length required for SQL Server index
    goal_type: Mapped[str] = mapped_column(String(50))  # 'daily' or 'weekly'

    entries = relationship("Entry", back_populates="habit", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=habit_categories, back_populates="habits")

class Entry(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"))
    date: Mapped[date_type] = mapped_column(Date)

    habit = relationship("Habit", back_populates="entries")
