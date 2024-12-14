# Import the registration function from start_handler.py
from handlers.start import register_start_handler
from aiogram import Bot, Dispatcher, types
from handlers.start import start


from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Call it when handlers are registered
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(start, commands=["admin","unban", "remove_admin", "add_admin", "promote", "ban", "stop_admin", "users", "admins", "stats", "promo", "add_promo", "stop", "events", "add_event", "update", "give_spin", "give_pass", "self_spin"])