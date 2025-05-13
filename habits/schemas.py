from datetime import datetime, date, time
from pydantic import BaseModel
from typing import Optional
from pydantic import ConfigDict


class HabitTrackerResponse(BaseModel):
    id: int
    date_mark: date

    model_config = ConfigDict(from_attributes=True)


class HabitResponse(BaseModel):
    id: int
    title: str
    repeat_period: str
    start_at: date
    today_mark: Optional[HabitTrackerResponse] = None
    reminder_time: Optional[time] = None

    model_config = ConfigDict(from_attributes=True)

class UnmarkedHabitResponse(BaseModel):
    id: int
    title: str
    repeat_period: str
    start_at: date

    # model_config = ConfigDict(from_attributes=True)

class HabitCreateRequest(BaseModel):
    title: str
    repeat_period: str
    start_at: date


class HabitUpdateRequest(BaseModel):
    title: Optional[str] = None
    repeat_period: Optional[str] = None
    start_at: Optional[date] = None

class ReminderUpdateRequest(BaseModel):
    chat_id: int
    time: time
    timezone: str
