import os
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Bot setup
BOT_TOKEN = "8178702211:AAFzHDX_22rch3R0yf4m-iLGgEz8iQDt0jo"
bot_directory = "/root/Aniverse/"  # Path to the directory where your bot files are stored
bot_script = "main.py"  # The main bot script
git_repo_url = "https://github.com/prister884/Aniverse.git"  # GitHub repo URL
tmux_session_name = "Aniverse"  # Name for the tmux session

# Initialize bot and dispatcher with MemoryStorage
storage = MemoryStorage()  # Initialize memory storage for temporary data
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)  # Link storage to the dispatcher

# Enable logging middleware
dp.middleware.setup(LoggingMiddleware())

# Create a reply keyboard with the Terminal button
TERMINAL_WEB_APP_URL = "https://shell.ptud.live"  # Replace with the actual web app URL

def get_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton(text="Terminal", web_app=WebAppInfo(url=TERMINAL_WEB_APP_URL))  # Opens the mini app
    )
    return keyboard

# Function to send log messages to the Telegram bot
async def send_log(message: str, callback_query: types.CallbackQuery):
    """Function to send log messages."""
    await callback_query.message.answer(message, reply_markup=get_reply_keyboard())

# Command to manage the bot
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Start Bot", callback_data="start_bot"),
        InlineKeyboardButton(text="Stop Bot", callback_data="stop_bot"),
        InlineKeyboardButton(text="Update Bot", callback_data="update_bot")
    )

    # Send a message with the management options and reply keyboard
    await message.answer(
        "Choose an option to manage the bot:", 
        reply_markup=keyboard
    )
    await message.answer(
        "You can also open the Terminal below:", 
        reply_markup=get_reply_keyboard()
    )

# Handle start bot action
@dp.callback_query_handler(lambda c: c.data == "start_bot")
async def manage_start_bot(callback_query: types.CallbackQuery):
    # Acknowledge the callback to prevent loading animation
    await callback_query.answer("Starting the bot...")

    # Perform the actual operation
    start_bot()
    await send_log("Bot has been started!", callback_query)

# Handle stop bot action
@dp.callback_query_handler(lambda c: c.data == "stop_bot")
async def manage_stop_bot(callback_query: types.CallbackQuery):
    # Acknowledge the callback to prevent loading animation
    await callback_query.answer("Stopping the bot...")

    # Perform the actual operation
    stop_bot()
    await send_log("Bot has been stopped!", callback_query)

# Handle update bot action
@dp.callback_query_handler(lambda c: c.data == "update_bot")
async def manage_update_bot(callback_query: types.CallbackQuery):
    # Acknowledge the callback to prevent loading animation
    await callback_query.answer("Updating the bot...")

    # Perform the actual operation
    update_bot()
    await send_log("Bot has been updated!", callback_query)

# Functions to start, stop, and update the bot
def start_bot():
    tmux_check = subprocess.run(f"tmux ls | grep {tmux_session_name}", shell=True, capture_output=True)
    if tmux_check.returncode == 0:  # If tmux session already exists
        return

    # Start the bot inside tmux
    tmux_command = f"tmux new-session -d -s {tmux_session_name} 'python {bot_directory}/{bot_script}'"
    subprocess.run(tmux_command, shell=True)

def stop_bot():
    subprocess.run(f"tmux kill-session -t {tmux_session_name}", shell=True)

def update_bot():
    stop_bot()  # Stop the bot first
    os.chdir(bot_directory)
    subprocess.run(["git", "pull"])  # Pull latest updates from GitHub
    subprocess.run(["pip", "install", "-r", "requirements.txt"])  # Install any new dependencies
    start_bot()  # Restart the bot after the update

# Run the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
