# Import the registration function from start_handler.py
from aiogram import Dispatcher
from aiogram import types

from handlers.admin import admin_commands, admin_message_handler
from handlers.back import back_to
from handlers.commands import start, leave_account, change_nickname
from handlers.craft import craft_all, use_craft
from handlers.rewards import claim_spins
from handlers.menu import handle_menu
from handlers.payment import payment_page_aniverse, alternative_payment
from handlers.process_callback import process_callback
from handlers.universe import choose_universe, paginate_universes, select_universe

from config import BOT_TOKEN
from dp import dp

# Call it when handlers are registered
def register_handlers(dp: Dispatcher):
    
    dp.register_message_handler(admin_commands, commands=["admin","unban", "remove_admin", "add_admin", "promote", "ban", "stop_admin", "users", "admins", "stats", "promo", "add_promo", "stop", "events", "add_event", "update", "give_spin", "give_pass", "self_spin"])
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(leave_account, commands=["leave"])
    dp.register_callback_query_handler(back_to, lambda c: c.data.startswith("back_to_"))
    dp.register_callback_query_handler(choose_universe, lambda c: c.data == "choose_universe")
    dp.register_callback_query_handler(paginate_universes, lambda c: c.data.startswith("page_"))
    dp.register_callback_query_handler(select_universe, lambda c: c.data.startswith("universe_"))
    dp.register_message_handler(change_nickname, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(craft_all, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(handle_menu, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(process_callback, lambda c: c.data in ["pass", "rating", "shop", "craft", "arena", "clans", "tasks", "referral", "change_universe", "spin_bonuses"])
    dp.register_callback_query_handler(use_craft, lambda c: c.data.startswith("craft_"))
    dp.register_callback_query_handler(claim_spins, lambda c: c.data.startswith("claim_spins"))
    dp.register_callback_query_handler(payment_page_aniverse, lambda c: c.data.startswith("payment_page_"))
    dp.register_callback_query_handler(alternative_payment, lambda c: c.data.startswith("alternative_payment_"))
    dp.register_message_handler(admin_message_handler, content_types=types.ContentTypes.TEXT)
