from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Annotated
from config import SECRET_KEY, ALGORITHM
from database.db_init import get_db
from database.db_utils import get_user_by_id
from database.models import User
from .schemas import TokenData
from config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)
# Настройка схемы безопасности OAuth2 с использованием Bearer токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict, secret_key: str, algorithm: str, expires_minutes: int):
    logger.debug(f"Start create_access_token")

    to_encode = data.copy()
    logger.debug(f"expires_minutes: {expires_minutes}")
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": int(expire.timestamp())})
    logger.debug(f"Token expire time (UTC): {expire} ({expire.timestamp()})")

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    logger.debug(f"Created token at UTC: {datetime.now(timezone.utc)}")
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug(f"Current UTC time at token check: {datetime.now(timezone.utc)}")
        logger.debug(f"Decoding token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Decoded payload: {payload}")
        user_id = payload.get("sub")
        if user_id is None:
            logger.debug("Token payload missing 'sub'")
            raise credentials_exception
        user_id = int(user_id)
        logger.debug(f"User ID from token: {user_id}")
    except JWTError as e:
        logger.debug(f"JWT decode error: {e}")
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if user is None:
        logger.debug(f"User with id {user_id} not found")
        raise credentials_exception
    logger.debug(f"User: {user}")
    return user