from aiogram.utils import executor
from handlers import register_handlers
from dp import dp

register_handlers(dp)
               
# Run the Bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
