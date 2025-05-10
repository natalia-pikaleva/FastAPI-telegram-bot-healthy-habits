from database.db_init import get_db
from database.db_utils import get_habit_by_id
from database.models import User, UserToken, Habit
from sqlalchemy import select
from sqlalchemy.orm import Session
from .schemas import HabitResponse, HabitCreateRequest
from auth.utils import create_access_token
from fastapi import Depends, APIRouter, status
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from config import setup_logging
import logging
from sqlalchemy.exc import SQLAlchemyError
import json
from typing import List, Any, Annotated
from auth.utils import get_current_user

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
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
    return {"message": "Habit created", "habit_id": new_habit.id}


@router.post("/{habit_id}/update", status_code=status.HTTP_200_OK)
def update_habit(
        habit: HabitCreateRequest,
        habit_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),

):
    logger.debug("Start update_habit")
    db_habit = get_habit_by_id(db, habit_id)
    db_habit.title = habit.title
    db_habit.repeat_period = habit.repeat_period
    db_habit.start_at = habit.start_at

    db.commit()
    db.refresh(db_habit)
    return {"message": "Habit updated", "habit_id": db_habit.id}


@router.delete("/{habit_id}/delete", status_code=status.HTTP_200_OK)
def delete_habit(
        habit_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),

):
    logger.debug("Start delete_habit")
    habit = get_habit_by_id(db, habit_id)
    db.delete(habit)
    db.commit()

    return {"message": "Habit deleted"}


@router.get("", response_model=List[HabitResponse])
def get_habits_list(
        db: Session = Depends(get_db),
        current_user: Any = Depends(get_current_user),
):
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return habits
