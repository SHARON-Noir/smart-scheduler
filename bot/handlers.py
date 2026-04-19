from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm your Smart Scheduler.\n\n"
        "Send me an event like:\n"
        "• 'Team meeting on 5 April at 4pm'\n"
        "• Or send a voice message!\n\n"
        "I'll handle the rest."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Got it! You said:\n_{user_text}_\n\n(AI parsing coming next phase)", parse_mode="Markdown")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voice received! Transcription coming in Phase 3.")