from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database.db_init import SessionLocal
from bot.setup import bot
from datetime import datetime, timedelta, timezone
from database.models import Reminder, Habit
import pytz

from bot.keyboards.inline.core import mark_habit

scheduler = BackgroundScheduler()


def send_reminders():
    db = SessionLocal()

    try:
        now_utc = datetime.now(timezone.utc)
        reminders = db.query(Reminder).all()

        for reminder in reminders:
            user_tz = pytz.timezone(reminder.timezone)
            now_local = now_utc.astimezone(user_tz).time().replace(second=0, microsecond=0)
            reminder_time = reminder.time.replace(second=0, microsecond=0)

            if now_local == reminder_time:
                habit = db.query(Habit).filter(Habit.id == reminder.habit_id).first()
                bot.send_message(
                    chat_id=reminder.chat_id,
                    text=f"⏰ Напоминание: пора выполнить привычку {habit.title}"
                )
                bot.send_message(
                    chat_id=reminder.chat_id,
                    text=f"Поставить отметку о выполнении?",
                    reply_markup=mark_habit(reminder.habit_id)
                )
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(send_reminders, CronTrigger(minute="*"))
    scheduler.start()
