from database.db_init import get_db
from database.db_utils import save_token_for_user
from database.models import User, UserToken
from sqlalchemy import select
from sqlalchemy.orm import Session
from routers.auth.schemas import AuthRequest, TokenResponse
from routers.auth.utils import create_access_token
from fastapi import Depends, APIRouter
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from config import setup_logging
import logging
from sqlalchemy.exc import SQLAlchemyError
import jwt

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def auth(auth_req: AuthRequest, db: Session = Depends(get_db)):
    logger.debug("Start router auth")
    user = db.execute(
        select(User).where(User.telegram_id == auth_req.telegram_id)
    ).scalars().one_or_none()

    if user is None:
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

    old_token = db.execute(select(UserToken).filter(UserToken.user_id == user.id)).scalars().first()

    if old_token:
        logger.debug("Delete okd token")

        db.delete(old_token)
        db.commit()


    token_data = {"sub": str(user.id)}
    access_token = create_access_token(
        data=token_data,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    logger.debug("Created token")
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    logger.debug(f"Decoded payload: {payload}")

    save_token_for_user(db, user, access_token)

    return {"access_token": access_token, "token_type": "bearer"}
