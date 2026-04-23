from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from db.database import get_pending_reminders, mark_reminder_sent

scheduler = AsyncIOScheduler()

async def check_reminders(app):
    events = get_pending_reminders()
    now = datetime.now()

    for event in events:
        event_id, chat_id, title, date, time, sent_1day, sent_1hour = event

        try:
            event_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        time_left = event_dt - now

        # 1 day before reminder
        if not sent_1day and timedelta(hours=23) <= time_left <= timedelta(hours=25):
            await app.bot.send_message(
                chat_id=chat_id,
                text=f"Reminder — Tomorrow!\n\n{title}\nDate: {date}\nTime: {time}"
            )
            mark_reminder_sent(event_id, "1day")
            print(f"Sent 1-day reminder for event {event_id}")

        # 1 hour before reminder
        if not sent_1hour and timedelta(minutes=55) <= time_left <= timedelta(minutes=65):
            await app.bot.send_message(
                chat_id=chat_id,
                text=f"Reminder — Starting in 1 hour!\n\n{title}\nDate: {date}\nTime: {time}"
            )
            mark_reminder_sent(event_id, "1hour")
            print(f"Sent 1-hour reminder for event {event_id}")