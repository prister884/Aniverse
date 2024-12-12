import logging
import subprocess
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your management bot token
MANAGEMENT_BOT_TOKEN = 'YOUR_MANAGEMENT_BOT_TOKEN'

# Target bot details
TARGET_BOT_DIRECTORY = '/root/Aniverse'
TARGET_BOT_SCRIPT = 'main.py'
TMUX_SESSION_NAME = 'Aniverse'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=MANAGEMENT_BOT_TOKEN)
dp = Dispatcher(bot)

# Utility function to execute shell commands
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            return f"Success: {result.stdout.strip()}"
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Exception: {str(e)}"

# Inline keyboard for commands
command_keyboard = InlineKeyboardMarkup(row_width=2)
command_keyboard.add(
    InlineKeyboardButton("Start", callback_data="start"),
    InlineKeyboardButton("Stop", callback_data="stop"),
    InlineKeyboardButton("Restart", callback_data="restart"),
    InlineKeyboardButton("Update", callback_data="update"),
    InlineKeyboardButton("Status", callback_data="status")
)

# Command handlers
@dp.message_handler(commands=['menu'])
async def show_menu(message: types.Message):
    await message.reply("Select an action:", reply_markup=command_keyboard)

@dp.callback_query_handler(lambda c: c.data in ["start", "stop", "restart", "update", "status"])
async def handle_command(callback_query: types.CallbackQuery):
    command_map = {
        "start": f"tmux new-session -d -s {TMUX_SESSION_NAME} 'cd {TARGET_BOT_DIRECTORY} && source venv/bin/activate && python {TARGET_BOT_SCRIPT}'",
        "stop": f"tmux kill-session -t {TMUX_SESSION_NAME}",
        "restart": f"tmux kill-session -t {TMUX_SESSION_NAME} && tmux new-session -d -s {TMUX_SESSION_NAME} 'cd {TARGET_BOT_DIRECTORY} && source venv/bin/activate && python {TARGET_BOT_SCRIPT}'",
        "update": f"cd {TARGET_BOT_DIRECTORY} && git pull && source venv/bin/activate && pip install -r requirements.txt",
        "status": f"tmux list-sessions | grep {TMUX_SESSION_NAME}"
    }

    command = command_map[callback_query.data]
    result = execute_command(command)

    # Customize status output
    if callback_query.data == "status":
        if "{TMUX_SESSION_NAME}" in result:
            result = "Bot is running in tmux."
        else:
            result = "Bot is not running."

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, result)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
