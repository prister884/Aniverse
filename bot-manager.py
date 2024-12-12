import logging
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Replace with your management bot token
MANAGEMENT_BOT_TOKEN = '8178702211:AAFzHDX_22rch3R0yf4m-iLGgEz8iQDt0jo'

# Target bot details
TARGET_BOT_DIRECTORY = '/root/Aniverse'
TARGET_BOT_SCRIPT = 'main.py'
TARGET_BOT_VENV = 'source venv/bin/activate'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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
def start_bot(update: Update, context: CallbackContext):
    command = f"cd {TARGET_BOT_DIRECTORY} && {TARGET_BOT_VENV} && nohup python {TARGET_BOT_SCRIPT} &"
    message = execute_command(command)
    update.message.reply_text(message)

def stop_bot(update: Update, context: CallbackContext):
    command = "pkill -f \"python /root/Aniverse/main.py\""
    message = execute_command(command)
    update.message.reply_text(message)

def restart_bot(update: Update, context: CallbackContext):
    stop_command = "pkill -f \"python /root/Aniverse/main.py\""
    start_command = f"cd {TARGET_BOT_DIRECTORY} && {TARGET_BOT_VENV} && nohup python {TARGET_BOT_SCRIPT} &"
    stop_message = execute_command(stop_command)
    start_message = execute_command(start_command)
    update.message.reply_text(f"Stop Command: {stop_message}\nStart Command: {start_message}")

def update_bot(update: Update, context: CallbackContext):
    update_command = f"cd {TARGET_BOT_DIRECTORY} && git pull"
    message = execute_command(update_command)
    update.message.reply_text(message)

def status_bot(update: Update, context: CallbackContext):
    command = "ps aux | grep \"python /root/Aniverse/main.py\" | grep -v grep"
    message = execute_command(command)
    if "python" in message:
        update.message.reply_text(f"Bot is running:\n{message}")
    else:
        update.message.reply_text("Bot is not running.")

def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text("Unknown command. Available commands: /start, /stop, /restart, /update, /status")

def main():
    # Create the Application and pass it the bot's token
    application = Application.builder().token(MANAGEMENT_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start_bot))
    application.add_handler(CommandHandler('stop', stop_bot))
    application.add_handler(CommandHandler('restart', restart_bot))
    application.add_handler(CommandHandler('update', update_bot))
    application.add_handler(CommandHandler('status', status_bot))

    # Handle unknown commands
    application.add_handler(CommandHandler('unknown', unknown_command))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()