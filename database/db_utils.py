import logging
from typing import List

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session
from config import setup_logging
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, User, UserToken
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
