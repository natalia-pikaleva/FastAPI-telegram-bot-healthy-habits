import bcrypt
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    _password = Column("password", String(255), index=True)

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
