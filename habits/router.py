from database.db_init import get_db
from database.db_utils import get_habit_by_id
from database.models import User, UserToken, Habit, HabitTracker, Reminder
from sqlalchemy import select
from sqlalchemy.orm import Session
from .schemas import HabitResponse, HabitCreateRequest, HabitUpdateRequest, ReminderUpdateRequest
from auth.utils import create_access_token
from fastapi import Depends, APIRouter, status
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from config import setup_logging
import logging
from sqlalchemy.exc import SQLAlchemyError
import json
from typing import List, Any, Annotated
from auth.utils import get_current_user
from datetime import date

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", status_code=HabitResponse)
def create_habit(
        habit: HabitCreateRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    logger.debug("Start create_habit")
    new_habit = Habit(
        title=habit.title,
        repeat_period=habit.repeat_period,
        start_at=habit.start_at,
        user_id=current_user.id
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)

    response = HabitResponse.from_orm(habit)
    return response


@router.post("/{habit_id}/update", response_model=HabitResponse)
def update_habit(
        habit: HabitUpdateRequest,
        habit_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),

):
    logger.debug("Start update_habit")
    db_habit = db.query(Habit).filter(Habit.id == habit_id).scalar()
    if habit.title:
        db_habit.title = habit.title
    if habit.repeat_period:
        db_habit.repeat_period = habit.repeat_period
    if habit.start_at:
        db_habit.start_at = habit.start_at

    db.commit()
    db.refresh(db_habit)

    today_mark = (
        db.query(HabitTracker)
        .filter(HabitTracker.habit_id == habit_id, HabitTracker.date_mark == date.today())
        .first()
    )
    response = HabitResponse.from_orm(habit)
    response.today_mark = today_mark
    return response


@router.delete("/{habit_id}/delete", status_code=status.HTTP_200_OK)
def delete_habit(
        habit_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),

):
    logger.debug("Start delete_habit")
    habit = db.query(Habit).filter(Habit.id == habit_id).scalar()
    db.delete(habit)
    db.commit()

    return {"message": "Habit deleted"}


@router.post("/{habit_id}/mark", response_model=HabitResponse)
def set_mark_on_habit(
        habit_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),

):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    response = HabitResponse.from_orm(habit)
    today_habit_mark = db.query(HabitTracker).filter(HabitTracker.habit_id == habit_id,
                                                     HabitTracker.date_mark == date.today()).first()

    if today_habit_mark:
        # Отметка за сегодня уже сделана, пользователь хочет убрать отметку
        response.today_mark = date.today()
        return response

    # Отметки за сегодня еще нет, ставим
    today_habit_mark = HabitTracker(
        habit_id=habit_id,
        date_mark=date.today()
    )
    db.add(today_habit_mark)
    db.commit()

    response.today_mark = date.today()
    return response


@router.post("/{habit_id}/set_reminder", status_code=status.HTTP_200_OK)
def set_reminder(
        habit_id: int,
        reminder: ReminderUpdateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),

):
    logger.debug(f"Start set_reminder with {reminder}")
    db_reminder = db.query(Reminder).filter(Reminder.chat_id == reminder.chat_id,
                                   Reminder.habit_id == habit_id).first()

    logger.debug(f"Reminder from db: {db_reminder}")

    if db_reminder:
        db_reminder.time = reminder.time
        db_reminder.timezone = reminder.timezone
        logger.debug("Update reminder")

    else:
        db_reminder = Reminder(
            habit_id=habit_id,
            chat_id=reminder.chat_id,
            time=reminder.time,
            timezone=reminder.timezone,
        )
        db.add(db_reminder)
        logger.debug("Create new reminder")

    db.commit()
    return {"message": "Time set for reminder"}


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
        habit_id: int,
        db: Session = Depends(get_db),
        current_user: Any = Depends(get_current_user),
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    today_mark = (
        db.query(HabitTracker)
        .filter(HabitTracker.habit_id == habit_id, HabitTracker.date_mark == date.today())
        .first()
    )
    response = HabitResponse.from_orm(habit)
    response.today_mark = today_mark
    reminder = db.query(Reminder).filter(Reminder.habit_id == habit.id).first()
    if reminder:
        response.reminder_time = reminder.time
    return response


@router.get("", response_model=List[HabitResponse])
def get_habits_list(
        db: Session = Depends(get_db),
        current_user: Any = Depends(get_current_user),
):
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return habits
