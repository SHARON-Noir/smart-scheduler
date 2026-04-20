from telegram import Update
from telegram.ext import ContextTypes
from bot.ai_parser import parse_event

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm your Smart Scheduler 🗓\n\n"
        "Send me an event like:\n"
        "• 'Team meeting on 5 April at 4pm'\n"
        "• 'Tomorrow 3pm project review'\n"
        "• Or send a voice message!\n\n"
        "I'll extract the details and remind you automatically."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("Parsing your event...")

    result = parse_event(user_text)

    if result:
        reply = (
            f"Got it! Here's what I understood:\n\n"
            f"Title: {result.get('title', 'N/A')}\n"
            f"Date: {result.get('date', 'N/A')}\n"
            f"Time: {result.get('time', 'N/A')}\n\n"
            f"Should I save this? (yes/no)"
        )
    else:
        reply = "Sorry, I couldn't understand that. Try something like 'Team meeting on 5 April at 4pm'."

    await update.message.reply_text(reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voice received! Transcription coming in Phase 3.")