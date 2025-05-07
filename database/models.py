import bcrypt
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    _password_hash = Column("password", String(255))
    username = Column(String(100), index=True, unique=True)
    first_name = Column(String(100), index=True)
    last_name = Column(String(100), index=True)

    chat_ids = relationship("Chat", back_populates="user", lazy="selectin")
    habits = relationship("Habit", back_populates="user", lazy="selectin")

    @property
    def password(self):
        raise AttributeError("Доступ к паролю запрещен")

    def set_password(self, raw_key: str):
        self._password_hash = bcrypt.hashpw(
            raw_key.encode(),
            bcrypt.gensalt()
        ).decode()

    def verify_password(self, raw_key: str) -> bool:
        if not hasattr(self, '_password_hash') or not self._password_hash:
            return False
        try:
            return bcrypt.checkpw(
                raw_key.encode(),
                self._password_hash.encode()
            )
        except (ValueError, AttributeError):
            return False


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="chat_ids", lazy="selectin")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), index=True)
    repeat_period = Column(String(100), index=True)
    start_at = Column(DateTime, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits", lazy="selectin")
