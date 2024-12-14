from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db import db

def get_universe_keyboard(page=1):
    """
    Generate a paginated inline keyboard for universes from MongoDB.
    """
    universes = db.universes.find()  # Fetch universes from MongoDB
    items_per_page = 7
    skip_items = (page - 1) * items_per_page
    universes = list(universes.skip(skip_items).limit(items_per_page))

    keyboard = InlineKeyboardMarkup(row_width=1)
    for universe in universes:
        keyboard.add(InlineKeyboardButton(universe["name"], callback_data=f"universe_{universe['name']}"))

    navigation_buttons = []
    navigation_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_welcome"))
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton("👆", callback_data=f"page_{page - 1}"))
    if len(universes) == items_per_page:
        navigation_buttons.append(InlineKeyboardButton("👇", callback_data=f"page_{page + 1}"))

    if navigation_buttons:
        keyboard.row(*navigation_buttons)


    return keyboard

