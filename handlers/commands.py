from config import BOT_TOKEN
from rate_limit import rate_limit
from db import db
from keyboards.main_keyboard import get_main_keyboard
from keyboards.welcome_button import get_welcome_buttons
from dp import dp
from handlers.craft import craft_all
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import datetime
from payment import alternative_payment


@rate_limit(1)
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    person_link = f"https://t.me/aniverseclonedonbot?start={user_id}"
    current_time = time.time()
    count_hour = 4

    # Check if the user exists in MongoDB
    user_data = db.users.find_one({"user_id": user_id})

    if user_data:

        universe = user_data.get("universe")

        # Check universe data if a universe is selected
        verse_data = None
        if universe:
            verse_data = db.universes.find_one({"name": universe})

        # User exists, greet them
        nickname = user_data.get("nickname", "Гость")
        username = user_data.get("username")
        await message.answer(
            f"👋 [{nickname}](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
            f"🃏 Цель игры в коллекционировании карточек. Собирай карточки и борись за место в топе \n\n"
            f"🌏 Вселенные будут постоянно обновляться и улучшаться",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(user_id),
            disable_web_page_preview=True  # Display main menu keyboard
        )


    else:

        banned_user_data = db.banned.find_one({"user_id":user_id})

        if not banned_user_data:

            # Add new user to MongoDB
            db.users.insert_one({
                "user_id": user_id,
                "username": username,
                "nickname": "Гость",
                "universe": "Не выбрана",  # No universe selected yet
                "cards": [[],[],[],[],[]],
                "seasonal_points": 0,
                "spin_chances": 1,
                "spins":1,
                "осколки":0,
                "обычные":0,
                "редкие":0,
                "эпические":0,
                "coins": 0,
                "last_drop":time.time(),
                "count_hour":4,
                "redeemed":[],
                "referral_count":0,
                "referral_link": person_link,
                "ref_spins": 0,
                "ref_redeemed": False,
                "player_status": 0,  # Indicates the number of days the Aniverse Pass is valid for
                "arena_notif": False,
                "spin_notif": False,
                "boss_notif": False,
                "is_admin": False,
                "register_date": datetime.now().strftime("%d.%m.%Y в %H:%M") if user_id != 5485208401 else "Никогда",
                "maximum_cards": 0  # Initially set to 0, updated after universe selection
            })
            
            
            # Greet the new user
            await message.answer(
                f"👋 [Гость](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
                f"🃏 Цель игры в коллекционировании карточек. Собирай карточки и борись за место в топе.\n\n"
                f"🗺 Для начала выбери вселенную, в которой будешь собирать карточки.",
                reply_markup=get_welcome_buttons(),
                parse_mode="Markdown",
                disable_web_page_preview=True  # Disable link preview for greeting message
            )

        else:

            unban_request = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="Подать заявку на разбан", url="https://t.me/aniverseclone_don"),
                InlineKeyboardButton(text="Разбан без проверки за 555 руб.", callback_data="alternative_payment")
            )

            # Greet the new user
            await message.answer(
                f"👋 [Гость](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
                f"🃏 К сожалению вы были забанены администраторами бота!\n",
                reply_markup=unban_request,
                parse_mode="Markdown",
                disable_web_page_preview=True  # Disable link preview for greeting message
            )

@rate_limit(1)
async def leave_account(message: types.Message):
    user_id = message.from_user.id

    # Check if the user exists in the database
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data:
        await message.answer("❌ У вас нет активной учетной записи для удаления.")
        return

    # Delete the user's data from the database
    db.users.delete_one({"user_id": user_id})
    
    await message.answer(
        "✅ Ваша учетная запись успешно удалена. Спасибо за использование Aniverse card! "
        "Если вы передумаете, вы всегда можете начать заново, используя команду /start."
    )

@rate_limit(1)
async def change_nickname(message: types.Message):
    """
    Allow the user to change their nickname with a text input like:
    Сменить ник НовыйНик
    """
    user_id = message.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    
    if not user_data:
        await message.answer("❌ Пожалуйста, сначала введите команду /start.")
        return

    # Check if the message starts with "Сменить ник"
    if message.text.lower().startswith("сменить ник"):

        # Extract the new nickname
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3 or not parts[2].strip():
            await message.answer("❌ Пожалуйста, укажите новый ник. Пример: Сменить ник НовыйНик")
            return

        new_nickname = parts[2].strip()

        # Update the user's nickname in the database
        db.users.update_one({"user_id": user_id}, {"$set": {"nickname": new_nickname}})
        
        await message.answer(f"👤 Твой ник изменён на: {new_nickname}")
    else:
        await craft_all(message)
 