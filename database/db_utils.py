import logging
from typing import List

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload, Session
from config import setup_logging
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, User, UserToken, Habit
import logging

setup_logging()
logger = logging.getLogger(__name__)


def get_user_by_chat_id(db: Session, chat_id: int) -> User:
    """Получение пользователя по id чата"""
    logger.debug("start get_user_by_chat_id")
    user = (db.execute(select(User)
                       .where(User.telegram_id == chat_id))).scalar()
    logger.debug(f"user: {user}")

    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Получение пользователя по его id"""
    logger.debug("start get_user_by_id")
    user = (db.execute(select(User)
                       .where(User.id == user_id))).scalar()
    logger.debug(f"user: {user}")

    return user


def get_token_for_user(db: Session, chat_id: int):
    """Получение токена пользователя"""
    logger.debug("start get_token_for_user")
    user = get_user_by_chat_id(db, chat_id)
    token = db.execute(
        select(UserToken.token)
        .where(UserToken.user_id == user.id)
        .order_by(desc(UserToken.id))  # сортируем по убыванию id, чтобы последний был первым
        .limit(1)
    ).scalar_one_or_none()
    return token


def save_token_for_user(db: Session, user: User, access_token):
    """Сохранение токена пользователя"""
    try:
        user_token = UserToken(user_id=user.id, token=access_token)
        db.add(user_token)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error saving token: {e}")


def get_habit_by_id(db: Session, habit_id: int) -> Habit:
    """Получение привычки по ее id"""
    logger.debug("start get_habit_by_id")
    habit = (db.execute(select(Habit)
                        .where(Habit.id == habit_id))).scalar()

    return habit
