from telegram import Update
from telegram.ext import ContextTypes
from bot.ai_parser import parse_event
from db.database import save_event, get_all_events
from db.database import save_event, get_all_events, delete_event

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm your Smart Scheduler\n\n"
        "Send me an event like:\n"
        "- 'Team meeting on 5 April at 4pm'\n"
        "- 'Tomorrow 3pm project review'\n"
        "- Or send a voice message!\n\n"
        "Commands:\n"
        "/events - see all your saved events\n"
        "/start - show this message"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.message.chat_id

    # handle yes/no confirmation
    if user_text.lower() in ["yes", "y"]:
        pending = context.user_data.get("pending_event")
        if pending:
            save_event(
                chat_id=chat_id,
                title=pending["title"],
                date=pending["date"],
                time=pending["time"]
            )
            context.user_data["pending_event"] = None
            await update.message.reply_text(
                f"Saved!\n\n"
                f"Title: {pending['title']}\n"
                f"Date: {pending['date']}\n"
                f"Time: {pending['time']}\n\n"
                f"I'll remind you 1 day before and 1 hour before."
            )
        else:
            await update.message.reply_text("No event to save. Send me an event first.")
        return

    if user_text.lower() in ["no", "n"]:
        context.user_data["pending_event"] = None
        await update.message.reply_text("Okay, event discarded. Send me a new one anytime.")
        return

    # parse new event
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
            "Try something like: 'Team meeting on 5 April at 4pm'"
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
            await update.message.reply_text(f"I heard: {text}\n\nParsing event...")
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
                reply = "I heard you but couldn't extract event details. Try again."

            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("Sorry, couldn't transcribe that. Please try again.")

    except Exception as e:
        print(f"Voice handler error: {e}")
        await update.message.reply_text("Something went wrong processing your voice message.")

async def list_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    events = get_all_events(chat_id)

    if not events:
        await update.message.reply_text("No events saved yet. Send me an event to get started!")
        return

    reply = "Your upcoming events:\n\n"
    for event in events:
        event_id, title, date, time = event
        reply += f"• {title}\n  Date: {date} | Time: {time}\n\n"

    await update.message.reply_text(reply)

async def list_events_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    events = get_all_events(chat_id)

    if not events:
        await update.message.reply_text("No events saved yet.")
        return

    reply = "Your saved events:\n\n"
    for event in events:
        event_id, title, date, time = event
        reply += f"ID {event_id} — {title}\n  Date: {date} | Time: {time}\n\n"

    reply += "To delete an event, send:\n/delete <ID>\n\nExample: /delete 1"
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
        await update.message.reply_text("Invalid ID. Example: /delete 1")
        return

    success = delete_event(event_id, chat_id)

    if success:
        await update.message.reply_text(f"Event {event_id} deleted successfully.")
    else:
        await update.message.reply_text(
            f"Could not find event {event_id}.\n"
            f"Use /events to see your saved events."
        )