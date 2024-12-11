import subprocess
import os
import signal
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Telegram bot token for the bot manager
BOT_TOKEN = "8178702211:AAFzHDX_22rch3R0yf4m-iLGgEz8iQDt0jo"
bot_directory = "/root/Aniverse/"  # Path to the directory where your bot is stored
bot_script = "main.py"  # Your main bot script name
git_repo_url = "https://github.com/prister884/Aniverse.git"  # Your Git repository URL
tmux_session_name = "Aniverse"  # tmux session name for the bot

# Initialize the bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Send log updates to the user
async def send_log(callback_query, message):
    try:
        await callback_query.answer(message)
    except Exception as e:
        await callback_query.answer(f"❌ Error: {str(e)}")

# Start Bot function using tmux
def start_bot(callback_query):
    # Check if tmux session already exists
    tmux_check = subprocess.run(f"tmux ls | grep {tmux_session_name}", shell=True, capture_output=True)
    if tmux_check.returncode == 0:  # If session exists
        return

    # Start the bot in a tmux session
    tmux_command = f"tmux new-session -d -s {tmux_session_name} 'python {bot_directory}/{bot_script}'"
    subprocess.run(tmux_command, shell=True)

    # Notify the user
    send_log(callback_query, "Bot has been started in tmux session.")

# Stop Bot function using tmux
def stop_bot(callback_query):
    # Kill the tmux session
    subprocess.run(f"tmux kill-session -t {tmux_session_name}", shell=True)
    
    # Notify the user
    send_log(callback_query, "Bot has been stopped.")

# Update Bot function using git and tmux
def update_bot(callback_query):
    # Notify user before starting the update
    send_log(callback_query, "Updating bot...")

    # Stop the bot before updating
    stop_bot(callback_query)

    # Go to the bot directory and update from GitHub
    os.chdir(bot_directory)
    subprocess.run(["git", "pull"])

    # Reinstall the virtual environment (if applicable)
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    # Start the bot again
    start_bot(callback_query)

# Bot command for managing the bot
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # Create an inline keyboard with bot management options
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Start Bot", callback_data="start_bot"),
        InlineKeyboardButton(text="Stop Bot", callback_data="stop_bot"),
        InlineKeyboardButton(text="Update Bot", callback_data="update_bot")
    )

    # Send a message with the management options
    await message.answer("Choose an option to manage the bot:", reply_markup=keyboard)

# Callback query handler for bot management
@dp.callback_query_handler(lambda c: c.data == "start_bot")
async def manage_start_bot(callback_query: types.CallbackQuery):
    start_bot(callback_query)
    await callback_query.answer("Bot has been started!")

@dp.callback_query_handler(lambda c: c.data == "stop_bot")
async def manage_stop_bot(callback_query: types.CallbackQuery):
    stop_bot(callback_query)
    await callback_query.answer("Bot has been stopped!")

@dp.callback_query_handler(lambda c: c.data == "update_bot")
async def manage_update_bot(callback_query: types.CallbackQuery):
    update_bot(callback_query)
    await callback_query.answer("Bot has been updated!")

# Main entry point for the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
