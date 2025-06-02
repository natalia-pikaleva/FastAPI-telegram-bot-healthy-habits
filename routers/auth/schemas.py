from pydantic import BaseModel


class AuthRequest(BaseModel):
    telegram_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None
