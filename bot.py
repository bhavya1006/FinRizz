from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


# Replace with your token later
# TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hi")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Catch all commands (like /start, /anything)
    app.add_handler(CommandHandler(command='start', callback=handle_command))

    app.run_polling()

if __name__ == "__main__":
    main()
