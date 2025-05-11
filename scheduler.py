from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database.db_init import SessionLocal
from bot.setup import bot
from datetime import datetime, timedelta, timezone
from database.models import Reminder
import pytz

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
                bot.send_message(
                    chat_id=reminder.chat_id,
                    text=f"⏰ Напоминание: пора выполнить привычки"
                )
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(send_reminders, CronTrigger(minute="*"))
    scheduler.start()
