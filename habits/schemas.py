from datetime import datetime
from pydantic import BaseModel


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
