from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db import db

# Main Menu Keyboard
def get_main_keyboard(user_id="none"):

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    
    admin_data = db.admins.find_one({"user_id":user_id})

    if not admin_data:
        keyboard.add(
            KeyboardButton("🥡 Получить карту"),
            KeyboardButton("🃏 Мои карты")
        )
        keyboard.add(
            KeyboardButton("☁ Меню"),
            KeyboardButton("⚙ Настройки")
        )

    else: 
        keyboard.add(
            KeyboardButton("🥡 Получить карту"),
            KeyboardButton("🃏 Мои карты")
        )
        keyboard.add(
            KeyboardButton("☁ Меню"),
            KeyboardButton("⚙ Настройки")
        )
        keyboard.add(
            KeyboardButton("😎 Админ панель")
        )

    return keyboard
