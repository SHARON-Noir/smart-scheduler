from telegram import Update
from telegram.ext import ContextTypes
from bot.ai_parser import parse_event
from db.database import save_event, get_all_events, delete_event
from datetime import date, datetime, timedelta

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm your Smart Scheduler\n\n"
        "Send me an event like:\n"
        "- 'Team meeting on 5 May at 4pm'\n"
        "- 'Tomorrow 3pm project review'\n"
        "- Or send a voice message!\n\n"
        "Commands:\n"
        "/events — see all saved events\n"
        "/today — events happening today\n"
        "/week — events this week\n"
        "/delete <ID> — delete an event\n"
        "/start — show this message"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.message.chat_id

    if user_text.lower() in ["yes", "y"]:
        pending = context.user_data.get("pending_event")
        if pending:
            save_event(
                chat_id=chat_id,
                title=pending["title"],
                date=pending["date"],
                time=pending["time"]
            )

            # immediate check — if event is within 2 hours, warn now
            from datetime import datetime
            if pending.get("date") and pending.get("time"):
                try:
                    event_dt = datetime.strptime(
                        f"{pending['date']} {pending['time']}",
                        "%Y-%m-%d %H:%M"
                    )
                    time_left = event_dt - datetime.now()
                    minutes_left = time_left.total_seconds() / 60

                    if 0 < minutes_left <= 60:
                        await update.message.reply_text(
                            f"Heads up — this event is in "
                            f"{int(minutes_left)} minutes!"
                        )
                    elif 60 < minutes_left <= 120:
                        await update.message.reply_text(
                            f"Note — this event is in about "
                            f"{int(minutes_left/60)} hour. "
                            f"You'll get a reminder soon."
                        )
                except:
                    pass

            # create google calendar event
            try:
                from bot.calendar_integration import create_calendar_event
                create_calendar_event(
                    pending["title"],
                    pending["date"],
                    pending["time"]
                )
                calendar_msg = "Added to Google Calendar!"
            except Exception as e:
                print(f"Calendar error: {e}")
                calendar_msg = "Could not add to Google Calendar."

            context.user_data["pending_event"] = None
            await update.message.reply_text(
                f"Saved!\n\n"
                f"Title: {pending['title']}\n"
                f"Date: {pending['date']}\n"
                f"Time: {pending['time']}\n\n"
                f"{calendar_msg}\n"
                f"Email + Telegram reminders set for 1 day before and 1 hour before."
            )
        else:
            await update.message.reply_text(
                "No pending event. Send me an event first."
            )
        return

    if user_text.lower() in ["no", "n"]:
        context.user_data["pending_event"] = None
        await update.message.reply_text(
            "Okay, discarded. Send me a new event anytime."
        )
        return

    await update.message.reply_text("Parsing your event...")
    result = parse_event(user_text)

    if result:
        context.user_data["pending_event"] = result
        reply = (
            f"Got it! Here's what I understood:\n\n"
            f"Title: {result.get('title', 'N/A')}\n"
            f"Date: {result.get('date', 'N/A')}\n"
            f"Time: {result.get('time', 'N/A')}\n\n"
            f"Should I save this? Reply yes or no."
        )
    else:
        reply = (
            "Sorry, I could not understand that.\n"
            "Try: 'Team meeting on 5 May at 4pm'"
        )

    await update.message.reply_text(reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voice received! Transcribing...")

    try:
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)

        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
        await file.download_to_drive(tmp.name)
        tmp.close()

        from bot.transcriber import transcribe_audio
        text = transcribe_audio(tmp.name)
        os.unlink(tmp.name)

        if text:
            await update.message.reply_text(
                f"I heard: {text}\n\nParsing event..."
            )
            result = parse_event(text)

            if result:
                context.user_data["pending_event"] = result
                reply = (
                    f"Got it! Here's what I understood:\n\n"
                    f"Title: {result.get('title', 'N/A')}\n"
                    f"Date: {result.get('date', 'N/A')}\n"
                    f"Time: {result.get('time', 'N/A')}\n\n"
                    f"Should I save this? Reply yes or no."
                )
            else:
                reply = (
                    "I heard you but couldn't extract event details.\n"
                    "Try saying: 'Team meeting on 5 May at 4pm'"
                )
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text(
                "Sorry, couldn't transcribe that. Please try again."
            )

    except Exception as e:
        print(f"Voice handler error: {e}")
        await update.message.reply_text(
            "Something went wrong processing your voice message."
        )

async def list_events_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    events = get_all_events(chat_id)

    if not events:
        await update.message.reply_text(
            "No events saved yet.\nSend me an event to get started!"
        )
        return

    reply = "Your saved events:\n\n"
    for event in events:
        event_id, title, date, time = event
        reply += f"ID {event_id} — {title}\n  Date: {date} | Time: {time}\n\n"

    reply += "To delete: /delete <ID>\nExample: /delete 1"
    await update.message.reply_text(reply)

async def delete_event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if not context.args:
        await update.message.reply_text(
            "Please provide an event ID.\n"
            "Example: /delete 1\n\n"
            "Use /events to see your event IDs."
        )
        return

    try:
        event_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "Invalid ID. Example: /delete 1"
        )
        return

    success = delete_event(event_id, chat_id)

    if success:
        await update.message.reply_text(
            f"Event {event_id} deleted successfully."
        )
    else:
        await update.message.reply_text(
            f"Could not find event {event_id}.\n"
            f"Use /events to see your saved events."
        )

async def today_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    events = get_all_events(chat_id)
    today = date.today().strftime("%Y-%m-%d")

    todays = [e for e in events if e[2] == today]

    if not todays:
        await update.message.reply_text(
            "No events today. Enjoy your free day!"
        )
        return

    reply = "Today's events:\n\n"
    for event in todays:
        event_id, title, event_date, time = event
        reply += f"• {title} at {time}\n"

    await update.message.reply_text(reply)

async def week_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    events = get_all_events(chat_id)

    today = date.today()
    week_later = today + timedelta(days=7)

    this_week = [
        e for e in events
        if e[2] and today.strftime("%Y-%m-%d") <= e[2] <= week_later.strftime("%Y-%m-%d")
    ]

    if not this_week:
        await update.message.reply_text(
            "No events this week. You're all clear!"
        )
        return

    reply = "Events this week:\n\n"
    for event in this_week:
        event_id, title, event_date, time = event
        reply += f"• {title}\n  Date: {event_date} | Time: {time}\n\n"

    await update.message.reply_text(reply)