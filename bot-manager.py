import logging
import subprocess
from aiogram import Bot, Dispatcher, executor, types

# Replace with your management bot token
MANAGEMENT_BOT_TOKEN = '8178702211:AAFzHDX_22rch3R0yf4m-iLGgEz8iQDt0jo'

# Target bot details
TARGET_BOT_DIRECTORY = '/root/Aniverse'
TARGET_BOT_SCRIPT = 'main.py'
TARGET_BOT_VENV = 'source venv/bin/activate'

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

# Command handlers
@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    command = f"cd {TARGET_BOT_DIRECTORY} && {TARGET_BOT_VENV} && nohup python {TARGET_BOT_SCRIPT} &"
    result = execute_command(command)
    await message.reply(result)

@dp.message_handler(commands=['stop'])
async def stop_bot(message: types.Message):
    command = f"pkill -f \"python {TARGET_BOT_DIRECTORY}/{TARGET_BOT_SCRIPT}\""
    result = execute_command(command)
    await message.reply(result)

@dp.message_handler(commands=['restart'])
async def restart_bot(message: types.Message):
    stop_command = f"pkill -f \"python {TARGET_BOT_DIRECTORY}/{TARGET_BOT_SCRIPT}\""
    start_command = f"cd {TARGET_BOT_DIRECTORY} && {TARGET_BOT_VENV} && nohup python {TARGET_BOT_SCRIPT} &"
    stop_result = execute_command(stop_command)
    start_result = execute_command(start_command)
    await message.reply(f"Stop Command: {stop_result}\nStart Command: {start_result}")

@dp.message_handler(commands=['update'])
async def update_bot(message: types.Message):
    update_command = f"cd {TARGET_BOT_DIRECTORY} && git pull && {TARGET_BOT_VENV} && pip install -r requirements.txt"
    result = execute_command(update_command)
    await message.reply(result)

@dp.message_handler(commands=['status'])
async def status_bot(message: types.Message):
    command = f"ps aux | grep \"python {TARGET_BOT_DIRECTORY}/{TARGET_BOT_SCRIPT}\" | grep -v grep"
    result = execute_command(command)
    if "python" in result:
        await message.reply(f"Bot is running:\n{result}")
    else:
        await message.reply("Bot is not running.")

@dp.message_handler()
async def unknown_command(message: types.Message):
    await message.reply("Unknown command. Available commands: /start, /stop, /restart, /update, /status")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
