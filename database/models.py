from datetime import date
from sqlalchemy import (Column, Integer, BigInteger, String, ForeignKey,
                        Date, UniqueConstraint, Time, ARRAY)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), index=True, unique=True)
    first_name = Column(String(100), index=True)
    last_name = Column(String(100), index=True)

    habits = relationship(
        "Habit",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan")
    tokens = relationship(
        "UserToken",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan")


class UserToken(Base):
    __tablename__ = "users_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(512), index=True, unique=True)

    user = relationship("User", back_populates="tokens", lazy="selectin")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), index=True)
    repeat_period = Column(String(100), index=True)
    week_days = Column(ARRAY(Integer))
    start_at = Column(Date, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits", lazy="selectin")
    dates = relationship(
        "HabitTracker",
        back_populates="habit",
        lazy="selectin",
        cascade="all, delete-orphan")
    reminder = relationship(
        "Reminder",
        back_populates="habit",
        lazy="selectin",
        cascade="all, delete-orphan")

    @property
    def date_mark(self):
        today = date.today()
        if today in set([tracker for tracker in self.dates]):
            return today
        return None

    @property
    def reminder_time(self):
        if self.reminder:
            return self.reminder.time
        return None


class HabitTracker(Base):
    __tablename__ = "habit_trackers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    date_mark = Column(Date, index=True)

    habit = relationship("Habit", back_populates="dates", lazy="selectin")

    __table_args__ = (
        UniqueConstraint('habit_id', 'date_mark', name='uq_habit_date'),
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    time = Column(Time)
    timezone = Column(String(50))
    chat_id = Column(BigInteger)

    habit = relationship("Habit", back_populates="reminder", lazy="selectin")
