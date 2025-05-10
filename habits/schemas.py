from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class HabitResponse(BaseModel):
    id: int
    title: str
    repeat_period: str
    start_at: datetime

    class Config:
        orm_mode = True


class HabitCreateRequest(BaseModel):
    title: str
    repeat_period: str
    start_at: datetime


class HabitUpdateRequest(BaseModel):
    title: Optional[str] = None
    repeat_period: Optional[str] = None
    start_at: Optional[datetime] = None
