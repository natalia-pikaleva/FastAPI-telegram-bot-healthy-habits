from database.db_init import get_db
from database.models import User, UserToken
from sqlalchemy import select
from sqlalchemy.orm import Session
from .schemas import AuthRequest, TokenResponse
from .utils import create_access_token
from fastapi import Depends, APIRouter
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from config import setup_logging
import logging
from sqlalchemy.exc import SQLAlchemyError

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def auth(auth_req: AuthRequest, db: Session = Depends(get_db)):
    logger.debug("Start router auth")
    user = db.execute(
        select(User).where(User.telegram_id == auth_req.telegram_id)
    ).scalar_one_or_none()

    if not user:
        logger.debug("User is None, start create User")
        user = User(telegram_id=auth_req.telegram_id)
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise

    token_data = {"sub": str(user.id)}
    access_token = create_access_token(
        data=token_data,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    logger.debug("Created token")
    try:
        user_token = UserToken(user_id=user.id, token=access_token)
        db.add(user_token)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error saving token: {e}")

    return {"access_token": access_token, "token_type": "bearer"}
