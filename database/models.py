import bcrypt
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100), index=True, unique=True)
    first_name = Column(String(100), index=True)
    last_name = Column(String(100), index=True)

    habits = relationship("Habit", back_populates="user", lazy="selectin")
    tokens = relationship("UserToken", back_populates="user", lazy="selectin")


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
    start_at = Column(Date, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits", lazy="selectin")
