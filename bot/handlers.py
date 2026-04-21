from telegram import Update
from telegram.ext import ContextTypes
from bot.ai_parser import parse_event

# store pending events per user
pending_events = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm your Smart Scheduler\n\n"
        "Send me an event like:\n"
        "- 'Team meeting on 5 April at 4pm'\n"
        "- 'Tomorrow 3pm project review'\n"
        "- Or send a voice message!\n\n"
        "I'll extract the details and remind you automatically."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text.strip().lower()

    # handle yes/no confirmation
    if user_id in pending_events:
        if user_text == "yes":
            event = pending_events.pop(user_id)
            await update.message.reply_text(
                f"Saved!\n\n"
                f"Title: {event.get('title', 'N/A')}\n"
                f"Date: {event.get('date', 'N/A')}\n"
                f"Time: {event.get('time', 'N/A')}\n\n"
                f"I'll remind you before the event."
            )
        elif user_text == "no":
            pending_events.pop(user_id)
            await update.message.reply_text("Cancelled. Send me another event anytime.")
        else:
            await update.message.reply_text("Please reply with yes or no.")
        return

    # parse new event
    await update.message.reply_text("Parsing your event...")
    result = parse_event(update.message.text)

    if result and result.get("title"):
        pending_events[user_id] = result
        reply = (
            f"Got it! Here's what I understood:\n\n"
            f"Title: {result.get('title', 'N/A')}\n"
            f"Date: {result.get('date', 'N/A')}\n"
            f"Time: {result.get('time', 'N/A')}\n\n"
            f"Should I save this? Reply yes or no."
        )
    else:
        reply = (
            "Sorry, I couldn't understand that.\n"
            "Try something like: 'Team meeting on 5 April at 4pm'"
        )

    await update.message.reply_text(reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
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

            if result and result.get("title"):
                pending_events[user_id] = result
                reply = (
                    f"Got it! Here's what I understood:\n\n"
                    f"Title: {result.get('title', 'N/A')}\n"
                    f"Date: {result.get('date', 'N/A')}\n"
                    f"Time: {result.get('time', 'N/A')}\n\n"
                    f"Should I save this? Reply yes or no."
                )
            else:
                reply = "I heard you but couldn't extract event details. Try saying something like 'Team meeting on 5 April at 4pm'."

            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("Sorry, I couldn't transcribe that. Please try again.")

    except Exception as e:
        print(f"Voice handler error: {e}")
        await update.message.reply_text("Something went wrong processing your voice message.")