from config import BOT_TOKEN
from rate_limit import ThrottlingMiddleware, rate_limit
from db import db
from keyboards.main_keyboard import get_main_keyboard
from keyboards.welcome_button import get_welcome_buttons

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import time
import datetime


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(ThrottlingMiddleware(default_rate_limit=2))


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
                InlineKeyboardButton(text="Подать заявку администратору", url="https://t.me/donshirley")
            )

            # Greet the new user
            await message.answer(
                f"👋 [Гость](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
                f"🃏 К сожалению вы были забанены администраторами бота!\n",
                reply_markup=unban_request,
                parse_mode="Markdown",
                disable_web_page_preview=True  # Disable link preview for greeting message
            )
