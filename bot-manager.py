import subprocess
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Bot setup
BOT_TOKEN = "8178702211:AAFzHDX_22rch3R0yf4m-iLGgEz8iQDt0jo"
bot_directory = "/root/Aniverse/"  # Path to the directory where your bot files are stored
bot_script = "main.py"  # The main bot script
git_repo_url = "https://github.com/prister884/Aniverse.git"  # GitHub repo URL
tmux_session_name = "Aniverse"  # Name for the tmux session
tmux_console_session = "console"  # Name for the tmux console session (for terminal commands)

# Initialize bot and dispatcher with MemoryStorage
storage = MemoryStorage()  # Initialize memory storage for temporary data
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)  # Link storage to the dispatcher

dp.middleware.setup(LoggingMiddleware())  # Enable logging middleware to capture errors and logs

# Function to send log messages to the Telegram bot
async def send_log(message: str, callback_query: types.CallbackQuery):
    """Function to send log messages."""
    await callback_query.message.answer(message, reply_markup=get_reply_keyboard())

# Create a reply keyboard with the terminal button and cancel button
def get_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton(text="Terminal"),  # Terminal button under the message bar
        KeyboardButton(text="Cancel")  # Cancel button to stop terminal session
    )
    return keyboard

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
    await message.answer("Choose an option to manage the bot:", reply_markup=keyboard)

# Handle terminal access when user presses "Terminal" button
@dp.message_handler(lambda message: message.text == "Terminal")
async def terminal_access(message: types.Message):
    # Ask user to enter the command to be executed in tmux
    await message.answer("Please enter the commands to be executed:")

    # Temporarily store the user ID to handle the message later
    await dp.storage.set_data(user=message.from_user.id, data={'waiting_for_command': True})

# Handle cancel session when user presses "Cancel"
@dp.message_handler(lambda message: message.text == "Cancel")
async def cancel_terminal(message: types.Message):
    # Cancel the terminal session and reset the state
    await dp.storage.set_data(user=message.from_user.id, data={'waiting_for_command': False})
    await message.answer("Terminal session has been canceled.", reply_markup=get_reply_keyboard())

# Handle receiving the command from the user
@dp.message_handler(lambda message: True)
async def execute_command(message: types.Message):
    user_id = message.from_user.id

    # Check if the user is in the state of "waiting for command"
    data = await dp.storage.get_data(user=user_id)
    if data.get('waiting_for_command', False):
        command = message.text  # The command entered by the user

        # Execute the command in the "console" tmux session
        try:
            # Start a new tmux session to run the command in the console tmux session
            tmux_command = f"tmux new-session -d -s {tmux_console_session} 'echo \"{command}\" | bash'"
            subprocess.run(tmux_command, shell=True)

            # Capture output from tmux (you can redirect tmux output to a file or capture it directly)
            output = subprocess.check_output(f"tmux capture-pane -p -t {tmux_console_session}", shell=True).decode()

            # Send the output to the user in Telegram
            await message.answer(f"Command executed successfully:\n{output}")

        except Exception as e:
            await message.answer(f"An error occurred: {e}")

        # After executing, reset the state
        await dp.storage.set_data(user=user_id, data={'waiting_for_command': False})

# Handle start bot action
@dp.callback_query_handler(lambda c: c.data == "start_bot")
async def manage_start_bot(callback_query: types.CallbackQuery):
    # Acknowledge the callback to prevent loading animation
    await callback_query.answer("Starting the bot...")

    # Perform the actual operation
    start_bot()
    await callback_query.message.answer("Bot has been started!")

# Handle stop bot action
@dp.callback_query_handler(lambda c: c.data == "stop_bot")
async def manage_stop_bot(callback_query: types.CallbackQuery):
    # Acknowledge the callback to prevent loading animation
    await callback_query.answer("Stopping the bot...")

    # Perform the actual operation
    stop_bot()
    await callback_query.message.answer("Bot has been stopped!")

# Handle update bot action
@dp.callback_query_handler(lambda c: c.data == "update_bot")
async def manage_update_bot(callback_query: types.CallbackQuery):
    # Acknowledge the callback to prevent loading animation
    await callback_query.answer("Updating the bot...")

    # Perform the actual operation
    update_bot()
    await callback_query.message.answer("Bot has been updated!")

# Run the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
