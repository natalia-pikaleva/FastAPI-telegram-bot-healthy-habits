from pydantic import BaseModel


class AuthRequest(BaseModel):
    telegram_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
