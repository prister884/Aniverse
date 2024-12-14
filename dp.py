from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from rate_limit import ThrottlingMiddleware


# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(ThrottlingMiddleware(default_rate_limit=2))