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

# Function to send logs to Telegram
async def send_log(message: str, callback_query: types.CallbackQuery):
    """Function to send log messages."""
    await callback_query.answer(message)

# Function to start the bot inside tmux
def start_bot():
    tmux_check = subprocess.run(f"tmux ls | grep {tmux_session_name}", shell=True, capture_output=True)
    if tmux_check.returncode == 0:  # If tmux session exists
        return

    # Start the bot in tmux
    tmux_command = f"tmux new-session -d -s {tmux_session_name} 'python {bot_directory}/{bot_script}'"
    subprocess.run(tmux_command, shell=True)

# Function to stop the bot in tmux
def stop_bot():
    subprocess.run(f"tmux kill-session -t {tmux_session_name}", shell=True)

# Function to update the bot using git
def update_bot():
    stop_bot()  # Stop the bot first
    os.chdir(bot_directory)
    subprocess.run(["git", "pull"])  # Update the bot from GitHub
    subprocess.run(["pip", "install", "-r", "requirements.txt"])  # Install any new requirements
    start_bot()  # Restart the bot after updating

# Command to manage the bot
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Start Bot", callback_data="start_bot"),
        InlineKeyboardButton(text="Stop Bot", callback_data="stop_bot"),
        InlineKeyboardButton(text="Update Bot", callback_data="update_bot")
    )
    await message.answer("Choose an option to manage the bot:", reply_markup=keyboard)

# Handle start bot action
@dp.callback_query_handler(lambda c: c.data == "start_bot")
async def manage_start_bot(callback_query: types.CallbackQuery):
    start_bot()
    await send_log("Bot has been started!", callback_query)

# Handle stop bot action
@dp.callback_query_handler(lambda c: c.data == "stop_bot")
async def manage_stop_bot(callback_query: types.CallbackQuery):
    stop_bot()
    await send_log("Bot has been stopped!", callback_query)

# Handle update bot action
@dp.callback_query_handler(lambda c: c.data == "update_bot")
async def manage_update_bot(callback_query: types.CallbackQuery):
    update_bot()
    await send_log("Bot has been updated!", callback_query)

# Run the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)