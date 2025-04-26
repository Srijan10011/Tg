
# Set up your API_ID, API_HASH, and bot token
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather



# Replace with your token
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your bot.')

def reply_to_message(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'You said: {update.message.text}')

def main():
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_to_message))

    # Start the bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
