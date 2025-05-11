from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from pydantic import ConfigDict


class HabitTrackerResponse(BaseModel):
    id: int
    date_mark: date

    class Config:
        orm_mode = True


class HabitResponse(BaseModel):
    id: int
    title: str
    repeat_period: str
    start_at: date
    today_mark: Optional[HabitTrackerResponse] = None

    model_config = ConfigDict(from_attributes=True)


class HabitCreateRequest(BaseModel):
    title: str
    repeat_period: str
    start_at: date


class HabitUpdateRequest(BaseModel):
    title: Optional[str] = None
    repeat_period: Optional[str] = None
    start_at: Optional[date] = None
