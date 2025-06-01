from collections import defaultdict
import datetime
from database.db_init import get_db
from database.models import User, Habit, HabitTracker, Reminder
from sqlalchemy import select, and_, or_, not_
from sqlalchemy.orm import Session, joinedload, aliased
from .schemas import HabitResponse, HabitCreateRequest, HabitUpdateRequest, ReminderUpdateRequest, \
    UnmarkedHabitResponse, HabitTrackerResponse
from fastapi import Depends, APIRouter, status, HTTPException
from config import setup_logging
import logging
from typing import List, Any
from ..auth.utils import get_current_user
from datetime import date

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", response_model=HabitResponse)
def create_habit(
        habit: HabitCreateRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    logger.debug("Start create_habit")
    try:
        new_habit = Habit(
            title=habit.title,
            repeat_period=habit.repeat_period,
            week_days=habit.week_days,
            start_at=habit.start_at,
            user_id=current_user.id
        )
        db.add(new_habit)
        db.commit()
        db.refresh(new_habit)

        response = HabitResponse.from_orm(new_habit)
        response.today_mark = None
        response.reminder_time = None

        if response.repeat_period == "daily":
            response.repeat_period = "Ежедневно"
        else:
            response.repeat_period = "Еженедельно"
        return response
    except Exception as e:
        logger.error("error during create habit %s", e)

@router.get("/unmarked", response_model=List[UnmarkedHabitResponse])
def get_unmarked_habits_list(
        db: Session = Depends(get_db),
        current_user: Any = Depends(get_current_user),
):
    try:
        day_index = date.today().weekday()

        # Выбираем привычки пользователя без отметок за сегодня, ежедневные или еженедельные,
        # у которых установлен текущий день недели
        habits = (db.query(Habit)
                  .filter(Habit.user_id == current_user.id,
                          not_(Habit.id.in_(
                              select(HabitTracker.habit_id)
                              .where(HabitTracker.date_mark == date.today())
                          )),
                          or_(
                              Habit.repeat_period == "daily",
                              and_(Habit.repeat_period == "weekly",
                                   Habit.week_days.any(day_index))
                          )
                          )
                  .options(
            joinedload(Habit.dates),
            joinedload(Habit.reminder)
        ).all())

        logger.error(f"habits: {habits}")

        return habits

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500)


@router.get("/statistics")
def get_statistics_habit_list(
        db: Session = Depends(get_db),
        current_user: Any = Depends(get_current_user),
):
    try:
        date_7_start = date.today() - datetime.timedelta(days=6)
        dates_week = [date_7_start + datetime.timedelta(days=i) for i in range(7)]

        habits = (db.query(Habit).filter(Habit.user_id == current_user.id)
                  .options(joinedload(Habit.dates)).all())

        logger.error(f"habits: {habits}")
        response = []

        for habit in habits:
            data = defaultdict()
            data["id"] = habit.id
            data["title"] = habit.title
            data["marked_days"] = [tracked.date_mark for tracked in habit.dates if tracked.date_mark > date_7_start]

            data["week"] = ''.join(['✅' if tracked in set(data["marked_days"])
                                    else '⚪️' for tracked in dates_week])

            response.append(data)

        return response

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500)


@router.get("/{habit_id}/statistics")
def get_statistics_by_habit_id(
        habit_id: int,
        db: Session = Depends(get_db),
        current_user: Any = Depends(get_current_user),
):
    try:
        date_21_start = date.today() - datetime.timedelta(days=20)
        dates_week = [date_21_start + datetime.timedelta(days=i) for i in range(21)]

        habit = (db.query(Habit).filter(Habit.id == habit_id)
                 .options(joinedload(Habit.dates)).scalar())

        result = {'title': habit.title}
        marked_days = [tracked.date_mark for tracked in habit.dates if tracked.date_mark > date_21_start]
        result['tracker'] = ''.join(['✅' if tracked in set(marked_days) else '⚪️' for tracked in dates_week])

        return result

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500)


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
    if habit.week_days:
        db_habit.week_days = habit.week_days
    if habit.start_at:
        db_habit.start_at = habit.start_at

    db.commit()
    db.refresh(db_habit)

    response = HabitResponse.from_orm(db_habit)
    if response.repeat_period == "daily":
        response.repeat_period = "Ежедневно"
    else:
        response.repeat_period = "Еженедельно"

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
        db.delete(today_habit_mark)
        db.commit()
        if response.repeat_period == "daily":
            response.repeat_period = "Ежедневно"
        else:
            response.repeat_period = "Еженедельно"
        return response

    # Отметки за сегодня еще нет, ставим
    today_habit_mark = HabitTracker(
        habit_id=habit_id,
        date_mark=date.today()
    )
    db.add(today_habit_mark)
    db.commit()

    if response.repeat_period == "daily":
        response.repeat_period = "Ежедневно"
    else:
        response.repeat_period = "Еженедельно"

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
    if response.repeat_period == "daily":
        response.repeat_period = "Ежедневно"
    else:
        response.repeat_period = "Еженедельно"

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

    today = date.today()
    today_tracker = aliased(HabitTracker)

    query = (
        db.query(Habit, today_tracker)
        .outerjoin(
            today_tracker,
            and_(
                Habit.id == today_tracker.habit_id,
                today_tracker.date_mark == today
            )
        )
        .filter(Habit.user_id == current_user.id)
    )

    results = query.all()

    habit_responses = []
    for habit, today_mark in results:
        habit_response = HabitResponse.from_orm(habit)

        if today_mark:
            habit_response.today_mark = HabitTrackerResponse.from_orm(today_mark)
        else:
            habit_response.today_mark = None

        habit_responses.append(habit_response)

    return habit_responses
