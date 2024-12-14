from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Inline Keyboard for Welcome Screen
def get_welcome_buttons():
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        
    InlineKeyboardButton("🌐 Выбрать вселенную", callback_data="choose_universe"),
    InlineKeyboardButton("➕ Добавить в чат", url="https://t.me/aniverseclonedonbot?startgroup=true")
    
    )
    
    return keyboard
 