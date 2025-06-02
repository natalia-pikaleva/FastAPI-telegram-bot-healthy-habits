from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date
from database.db_init import SessionLocal
from bot.setup import bot
from datetime import datetime, timezone
from database.models import Reminder, Habit, HabitTracker
import pytz
from sqlalchemy import and_, or_, not_, select

from bot.keyboards.inline.core import mark_habit

scheduler = BackgroundScheduler()


def send_reminders():
    db = SessionLocal()

    try:
        now_utc = datetime.now(timezone.utc)
        reminders = db.query(Reminder).all()

        today = date.today()
        day_index = today.weekday()

        for reminder in reminders:
            user_tz = pytz.timezone(reminder.timezone)
            now_local = now_utc.astimezone(user_tz).time().replace(second=0, microsecond=0)
            reminder_time = reminder.time.replace(second=0, microsecond=0)

            if now_local == reminder_time:
                habit = (db.query(Habit)
                         .filter(Habit.id == reminder.habit_id,
                                 not_(Habit.id.in_(
                                     select(HabitTracker.habit_id)
                                     .where(HabitTracker.date_mark == today)
                                 )),
                                 or_(
                                     Habit.repeat_period == "daily",
                                     and_(Habit.repeat_period == "weekly",
                                          Habit.week_days.any(day_index))
                                 )
                            )
                         .first())

                if not habit is None:
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
