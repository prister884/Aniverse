from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
import locale
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
import asyncio

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_rate_limit=1):
        super(ThrottlingMiddleware, self).__init__()
        self.default_rate_limit = default_rate_limit
        self.cache = {}

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        handler = data.get("handler")
        handler_name = handler.__name__ if handler else "global"
        rate_limit = getattr(handler, "rate_limit", self.default_rate_limit)
        current_time = asyncio.get_event_loop().time()

        # Throttling logic
        user_cache = self.cache.setdefault(user_id, {})
        if handler_name in user_cache and current_time < user_cache[handler_name] + rate_limit:
            remaining_time = round(user_cache[handler_name] + rate_limit - current_time, 2)
            raise Throttled
        user_cache[handler_name] = current_time

def rate_limit(limit=1):
    """
    Rate limit decorator for handlers.
    """
    def decorator(func):
        func.rate_limit = limit
        return func
    return decorator

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(ThrottlingMiddleware(default_rate_limit=2))