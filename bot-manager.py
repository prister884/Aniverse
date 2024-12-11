import subprocess
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Bot setup
BOT_TOKEN = "8178702211:AAFzHDX_22rch3R0yf4m-iLGgEz8iQDt0jo"
bot_directory = "/root/Aniverse/"  # Path to the directory where your bot files are stored
bot_script = "main.py"  # The main bot script
git_repo_url = "https://github.com/prister884/Aniverse.git"  # GitHub repo URL
tmux_session_name = "Aniverse"  # Name for the tmux session

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Function to send log messages to the Telegram bot
async def send_log(message: str, callback_query: types.CallbackQuery):
    """Function to send log messages."""
    await callback_query.message.answer(message, reply_markup=get_reply_keyboard())

# Create a reply keyboard with the terminal button
def get_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton(text="Terminal")  # Terminal button under the message bar
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

    # Set the user's state to "waiting for command" (this step can be managed using FSM if necessary)
    # Temporarily store the user ID to handle the message later
    await dp.storage.set_data(user=message.from_user.id, data={'waiting_for_command': True})

# Handle receiving the command from the user
@dp.message_handler(lambda message: True)
async def execute_command(message: types.Message):
    user_id = message.from_user.id

    # Check if the user is in the state of "waiting for command"
    data = await dp.storage.get_data(user=user_id)
    if data.get('waiting_for_command', False):
        command = message.text  # The command entered by the user

        # Execute the command in tmux
        try:
            # Start a new tmux session to run the command
            tmux_command = f"tmux new-session -d 'echo \"{command}\" | bash'"
            subprocess.run(tmux_command, shell=True)

            # Capture output from tmux (you can redirect tmux output to a file or capture it directly)
            output = subprocess.check_output(f"tmux capture-pane -p -t {tmux_session_name}", shell=True).decode()

            # Send the output to the user in Telegram
            await message.answer(f"Command executed successfully:\n{output}")
        except Exception as e:
            await message.answer(f"An error occurred: {e}")

        # After executing, reset the state
        await dp.storage.set_data(user=user_id, data={'waiting_for_command': False})

# Run the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
