import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import (
    start, handle_text, handle_voice,
    list_events_delete, delete_event_handler,
    today_events, week_events
)
from db.database import init_db
from bot.scheduler import scheduler, check_reminders

load_dotenv()

async def post_init(app):
    from apscheduler.triggers.interval import IntervalTrigger
    scheduler.add_job(
        check_reminders,
        trigger=IntervalTrigger(minutes=1),
        args=[app],
        id="reminder_check",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started — checking reminders every minute.")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN not found in .env file")

    init_db()
    print("Database initialized.")

    app = (
        ApplicationBuilder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("events", list_events_delete))
    app.add_handler(CommandHandler("delete", delete_event_handler))
    app.add_handler(CommandHandler("today", today_events))
    app.add_handler(CommandHandler("week", week_events))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()