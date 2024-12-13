import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from pymongo import MongoClient
from aiogram.utils.exceptions import MessageToDeleteNotFound
from datetime import datetime
import locale
import random
from aiogram.types import InputFile
import time
import asyncio
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from functools import wraps
import subprocess
import sys
import os



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

# mongodb+srv://abdurazzoqov057:YphGIIaGnFWHI1Ja@cluster0.m0r1q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

# MongoDB connection
client = MongoClient("mongodb+srv://abdurazzoqov057:yqW7tgxtYjcROPkM@cluster0.ttusl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.aniverse_db  # Use your database name

# Bot Token
BOT_TOKEN = "7934666713:AAFbgdmmSEYY-MGSmSmUAEIYvZVTG8tdbSk"

# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


dp.middleware.setup(ThrottlingMiddleware(default_rate_limit=2))


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@rate_limit(2)
@dp.message_handler(commands=["update"])
async def update_bot(message: types.Message):
    user_id = message.from_user.id
    admin_data = db.admins.find_one({"user_id":user_id})

    # Check if the user is authorized
    if not admin_data or admin_data.get("role") != "owner":
        await message.answer("🚫 Вы не авторизованы или не являетесь администратором.")
        return

    await message.answer("🔄 Обновление бота... Пожалуйста подождите.")

    # Pull latest changes from GitHub
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, check=True)
        git_output = result.stdout
    except subprocess.CalledProcessError as e:
        await message.answer(f"❌ Не удалось получить обновления с GitHub:\n{e.stderr}")
        return

    await message.answer(f"✅ Обновления синхронизированы:\n`\n{git_output}\n`", parse_mode="Markdown")

    # Restart the bot
    if git_output != "Already up to date.":
        try:
            await message.answer("♻️ Перезапускаю бота...")
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            await message.answer(f"❌ Не удалось перезапустить бота:\n{e}")

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

# Inline Keyboard for Welcome Screen
def get_welcome_buttons():
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        
    InlineKeyboardButton("🌐 Выбрать вселенную", callback_data="choose_universe"),
    InlineKeyboardButton("➕ Добавить в чат", url="https://t.me/aniverseclonedonbot?startgroup=true")
    
    )
    
    return keyboard
    
@rate_limit(1)
# Handle Start Command
@dp.message_handler(commands=["start"])
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
        await message.answer(
            f"👋 [{nickname}](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
            f"🃏 Цель игры в коллекционировании карточек. Собирай карточки и борись за место в топе \n\n"
            f"🌏 Вселенные будут постоянно обновляться и улучшаться",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(user_id)  # Display main menu keyboard
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


@rate_limit(1)
@dp.message_handler(commands=["leave"])
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
@dp.callback_query_handler(lambda c: c.data.startswith("back_to_"))
async def back_to(callback_query: types.CallbackQuery):
    """
    Handle the "back" button for various screens.
    The function dynamically checks the callback data and navigates to the appropriate screen.
    """
    # Acknowledge the callback to prevent the Telegram "waiting" state


    await callback_query.answer()


    user_id = callback_query.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    nickname = user_data.get("nickname", "Гость")
    spin_chances = user_data.get("spin_chances", 0)
    universe = user_data.get("universe", "Не выбрана")
    seasonal_points = user_data.get("seasonal_points", 0)
    register_date = user_data.get("register_date")
    player_status = user_data.get("player_status")
    coins = user_data.get("coins")
    cards = user_data.get("cards", [[],[],[],[],[]])
    verse_data = db.universes.find_one({"name":universe})
    user_data = db.users.find_one({"user_id": user_id})

    maximum = verse_data.get("maximum", [])
    maximum_casual = maximum[1]
    maximum_rare = maximum[2]
    maximum_epic = maximum[3]
    maximum_legendary = maximum[4]
    maximum_mythic = maximum[5]
    
    casual_cards = len(cards[0])
    rare_cards = len(cards[1])
    epic_cards = len(cards[2])
    legendary_cards = len(cards[3])
    mythic_cards = len(cards[4])
    card_count = casual_cards+rare_cards+epic_cards+legendary_cards+mythic_cards

    # Extract the type of the back action from the callback data
    back_type = callback_query.data.split("_", 2)[2]  # Extract the part after "back_to_"

    if back_type == "welcome":
        # Handle back to welcome screen
        user_id = callback_query.from_user.id
        user_data = db.users.find_one({"user_id": user_id})
        if not user_data:
            await callback_query.answer("❌ Пожалуйста, сначала введите команду /start.")
            return

        await callback_query.message.edit_text(
            "👋 Добро пожаловать в Aniverse card! Для начала выбери вселенную.",
            reply_markup=get_welcome_buttons(),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    elif back_type == "aniverse":
        # Handle back to Aniverse screen (you can add logic specific to this screen)
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(text="🔑 Купить Aniverse pass", callback_data="payment_page_aniverse_pass")
        )
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
        )

        await callback_query.message.edit_text(
            f"🔓 Что даст тебе Aniverse pass? \n\n"
            f"⛺️ Возможность создать свой собственный клан \n"
            f"⌛️ Возможность получать карточки каждые 3 часа вместо 4 \n"
            f"🏟 Возможность сражаться на арене каждый час вместо 2 \n"
            f"🕒 Уведомления об окончании времени ожидания карт и арены \n"
            f"👾 Уведомления об окончании времени сражения с боссом \n"
            f"🃏 Повышенная вероятность выпадения легендарных, эпических и мифических карт \n"
            f"👤 Возможность использовать смайлики в никнейме \n"
            f"🥡 Получишь +3 крутки \n"
            f"🗓️ Срок действия 30 дней \n \n"
            f"🔑 Aniverse pass - 159 рублей ",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    elif back_type == "menu":

        # Handle "Меню"
        
        keyboard = InlineKeyboardMarkup(row_width=2)

        # First row
        keyboard.add(
            InlineKeyboardButton(text="🔑 Pass", callback_data="pass"),
            InlineKeyboardButton(text="🏆 Рейтинг", callback_data="rating"),
        )

        # Second row
        keyboard.add(
            InlineKeyboardButton(text="🔮 Магазин", callback_data="shop"),
            InlineKeyboardButton(text="♻️ Крафт", callback_data="craft")
        )

        # Third row
        keyboard.add(
            InlineKeyboardButton(text="⛺️ Кланы", callback_data="clans"),
            InlineKeyboardButton(text="🏟 Арена", callback_data="arena")
        )

        # Fourth row
        keyboard.add(
            InlineKeyboardButton(text="🌙 Задания", callback_data="tasks"),
            InlineKeyboardButton(text="🔗 Рефералка", callback_data="referral")
        )
        
        # Fifth row
        
        keyboard.add(
            InlineKeyboardButton(text="🗺️ Сменить вселенную", callback_data="change_universe")   
        )
        
        keyboard.add(
            InlineKeyboardButton(text="🎁 Бонусы за Крутки", callback_data="spin_bonuses")
        )
        
        universe_cut = universe.split(" ", 1)[1] if universe != "Не выбрана" else universe
        
        cards_count = casual_cards+rare_cards+epic_cards+legendary_cards+mythic_cards


        await callback_query.message.edit_text(
            f"👤 Ник: [{nickname}](tg://user?id={user_id}) \n"
            f"🗺️ Вселенная: {universe_cut} \n"
            f"🃏 Всего карт: {cards_count} из {maximum[0]}\n"
            f"🎖️ Сезонные очки: {seasonal_points} _pts_ \n"
            f"💰 Коины: {coins} 🪙", 
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    elif back_type == "paymentaniverse":
        
        # Acknowledge the callback
        await callback_query.answer()
        
        keys = InlineKeyboardMarkup(row_width=2)

        keys.add(
                InlineKeyboardButton(text="🛒 Оплатить", callback_data="alternative_payment_aniverse_aniverse_pass"),
                InlineKeyboardButton(text="✅ Я оплатил", callback_data="payment_completed")
        )
        
        keys.add(
                InlineKeyboardButton(text="✏️ Другие Способы", callback_data="alternative_payment_aniverse_aniverse_pass")  
        )
        
        keys.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_aniverse")
        )
    
        await callback_query.message.edit_text(
            f"🧾 Покупка Aniverse pass\n"
            f"💵 Стоимость: 159 рублей \n"
            f"➖➖➖➖➖➖\n"
            f"‼️ `После оплаты нажми кнопку \"я оплатил\"`.\n\n"
            f"💬 `Возникли сложности с донатом? Пиши сюда - @donshirley` \n"
            f"➖➖➖➖➖➖\n"
            f"[Пользовательское соглашение](https://telegra.ph/Polzovatelskoe-soglashenie-06-01-5)",
            parse_mode="Markdown",
            reply_markup=keys,
            disable_web_page_preview=True
        )


    else:
        # Handle other back actions here, if any
        await callback_query.message.edit_text(
            "❌ Неизвестная команда. Пожалуйста, выберите доступный вариант из меню.",
            parse_mode="Markdown"
        )
    
    # Acknowledge the callback to ensure the transition is visible to the user
    await callback_query.answer()


@rate_limit(1)
# Handle Choose Universe
@dp.callback_query_handler(lambda c: c.data == "choose_universe")
async def choose_universe(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Ensure the user exists
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data:
        await callback_query.answer("❌ Пожалуйста, сначала введите команду /start.")
        return

    # Display the first page of universes
    await callback_query.message.edit_text(
        "🌌 Выберите вселенную из списка ниже:",
        reply_markup=get_universe_keyboard(page=1)
    )

@rate_limit(1)
# Handle Paginate Universes
@dp.callback_query_handler(lambda c: c.data.startswith("page_"))
async def paginate_universes(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[1])  # Extract page number
    await callback_query.message.edit_text(
        "🌌 Выберите вселенную из списка ниже:",
        reply_markup=get_universe_keyboard(page=page)
    )

@rate_limit(1)
@dp.callback_query_handler(lambda c: c.data.startswith("universe_"))
async def select_universe(callback_query: types.CallbackQuery):
    """
    Handle user universe selection and save it to the database.
    """
    user_id = callback_query.from_user.id
    universe_name = callback_query.data.split("_", 1)[1]  # Extract universe name
    user_data = db.users.find_one({"user_id":user_id})

    # Fetch universe data to get maximum number of cards
    verse_data = db.universes.find_one({"name": universe_name})
    maximum_cards = verse_data.get("maximum", []) if verse_data else []

    # Update the user's selected universe and maximum cards in MongoDB
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"universe": universe_name, "maximum_cards": maximum_cards[0]}}
    )
    
    # Acknowledge the callback
    await callback_query.answer()

    # Confirm the selection
    user_data = db.users.find_one({"user_id": user_id})
    nickname = user_data.get("nickname", "Гость")
    user_link = f"[{nickname}](tg://user?id={user_id})"

    # Correct the keyboard and message
    await callback_query.message.edit_text(
        f"🏔 [{nickname}](tg://user?id={user_id}), твоя выбранная вселенная: {universe_name}.\n ➖➖➖➖➖➖ \n"
        f"🥡 Чтобы получить карту, напиши команду \"`Получить карту`\".",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
    
    await callback_query.message.answer(
        f"🏔 [{nickname}](tg://user?id={user_id}), твоя выбранная вселенная: {universe_name}.\n ➖➖➖➖➖➖ \n"
        f"🥡 Чтобы получить карту, напиши команду \"`Получить карту`\".",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=get_main_keyboard(user_id)  # Show main keyboard after universe selection
    )
    
    # Delete the greeting message after a short delay (e.g., 2 seconds)
    try:
        await callback_query.message.delete()  # Delete the message after sending
    except MessageToDeleteNotFound:
        pass  # Handle the case when the message is already deleted (i.e., no error)

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



@rate_limit(1)
@dp.message_handler(content_types=types.ContentTypes.TEXT)
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

    # Continue with other menu options if "Сменить ник" is not detected
    else:
        await handle_menu(message)


@rate_limit(0.5)
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_menu(message: types.Message):
    """
    Handle actions from the reply keyboard menu under the message bar.
    """
    user_id = message.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    nickname = user_data.get("nickname", "Гость")
    spin_chances = user_data.get("spin_chances", 0)
    universe = user_data.get("universe", "Не выбрана")
    seasonal_points = user_data.get("seasonal_points", 0)
    register_date = user_data.get("register_date")
    player_status = user_data.get("player_status")
    coins = user_data.get("coins")
    cards = user_data.get("cards", [[],[],[],[],[]])
    verse_data = db.universes.find_one({"name":universe})
    user_data = db.users.find_one({"user_id": user_id})

    casual_cards = len(cards[0])
    rare_cards = len(cards[1])
    epic_cards = len(cards[2])
    legendary_cards = len(cards[3])
    mythic_cards = len(cards[4])
    card_count = casual_cards+rare_cards+epic_cards+legendary_cards+mythic_cards

    maximum = verse_data.get("maximum", [])
    maximum_casual = maximum[1]
    maximum_rare = maximum[2]
    maximum_epic = maximum[3]
    maximum_legendary = maximum[4]
    maximum_mythic = maximum[5]
    


    if not user_data:
        await message.answer("❌ Пожалуйста, сначала введите команду /start.")
        return

    # Normalize the text to handle case-insensitive matches
    user_input = message.text.strip().lower()

    if "получить карту" in user_input:

        count_hour = user_data.get("count_hour", 4)

        # Assuming user_data is already defined, and spin_chances is initialized
        start_time = user_data.get("last_drop", time.time())  # Get last drop time in seconds
        count_seconds = count_hour * 3600  # 4 hours in seconds

        # Get the current time
        current_time = time.time()  # Get the current time in seconds
        elapsed_time = current_time - start_time  # Calculate elapsed time

        # Calculate remaining time
        remaining_time = count_seconds - elapsed_time
        remaining_hours = int(remaining_time // 3600)
        remaining_minutes = int((remaining_time % 3600) // 60)
        remaining_seconds = int(remaining_time % 60)

        if spin_chances>0 or elapsed_time >= count_seconds:

            # Deduct a spin chance
            spin_chances = user_data.get("spin_chances", 0)
            spin_chances = spin_chances-1 if user_id != 5485208401 else spin_chances
            spins = user_data.get("spins",0)
            spins += 1

            # Update the spin chances in the database
            db.users.update_one({"user_id": user_id}, {"$set": {"spin_chances": spin_chances, "last_drop":current_time, "spins":spins}})


            if user_data:
                numbers = list(range(1, maximum[0]+1))
            
                # Weights for each range
                weights = []

                # Assign weights based on the described probabilities
                for num in numbers:
                    if 1 <= num <= maximum_casual:
                        weights.append(2)  # Twice the probability of the next range
                    elif maximum_casual+1 <= num <= maximum_rare:
                        weights.append(1.5)  # Normal probability
                    elif maximum_rare+1 <= num <= maximum_epic:
                        weights.append(1)  # Half the probability of the previous range
                    elif maximum_epic+1 <= num <= maximum_legendary:
                        weights.append(0.5)  # Half the probability of the previous range
                    else:
                        weights.append(0.15)  # Quarter of the probability of the previous range
                
                random_number = random.choices(numbers, weights=weights, k=1)[0]

                universes = {        
                    "🪸 Ван пис":"onepiece_data",
                    "🍀 Чёрный клевер":"blackclever_data",
                    "🗡 Блич":"bleach_data",
                    "🍥 Наруто":"naruto_data",
                    "🎩 ДжоДжо":"jojo_data",
                    "🐜 Хантер × Хантер":"hunterxhunter_data",
                    "🥀 Токийский Гуль":"tokyog_data",
                    "👊 Ванпанчмен":"onepunchman_data",
                    "👺 Истребитель демонов":"demonslayer_data",
                    "🪚 Человек бензопила":"chainsawman_data",
                    "🍎 Повесть о конце света":"judgedaynotice_data",
                    "⚽️ Синяя тюрьма":"bluelock_data",
                    "🪄 Магическая битва":"magicfight_data",
                    "🧤 Моя геройская академия":"myheroacademy_data",
                    "🐷 Семь смертных грехов":"sevensins_data",
                    "⚔️ Берсерк":"berserk_data",
                    "🩻 Атака титанов":"titanattack_data",
                    "📓 Тетрадь смерти":"deathnote_data",
                    "🧚 Хвост феи":"fairytail_data",
                    "☀️ Сага о Винланде":"winlandsaga_data",
                    "⏱️ Токийские мстители":"tokyoavengers_data",
                    "🔮 Моб Психо 100":"mobpsycho100_data",
                    "⚾️ Покемон":"pokemon_data",
                    "☄️ Драгонболл":"dragonball_data",
                    "♟ Сололевелинг":"sololevelling_data"
                }

                # Validate the universe exists
                if universe in universes:
                    collection_name = universes[universe]  # Get the corresponding collection name
                    card_data = db[collection_name].find_one({"id": random_number})  # Query the database
                else:
                    pass


                card_name = card_data.get("name")
                card_rarity = card_data.get("rarity")
                card_attack = card_data.get("attack")
                card_health = card_data.get("health")
                card_value = card_data.get("value")
                card_img_url = card_data.get("image_url")
                cards = user_data.get("cards",[[],[],[],[],[]])
                flattened_cards = [item for sublist in cards for item in sublist]


                if random_number not in flattened_cards:

                    if card_rarity == "Обычная":
                        cards[0].append(random_number)
                    elif card_rarity == "Редкая":
                        cards[1].append(random_number)
                    elif card_rarity == "Эпическая":
                        cards[2].append(random_number)
                    elif card_rarity == "Легендарная":
                        cards[3].append(random_number)
                    elif card_rarity == "Мифическая":
                        cards[4].append(random_number)


                    db.users.update_one({"user_id":user_id},{"$set": {"cards":cards, "seasonal_points":seasonal_points+card_value, "coins":coins+card_value}})

                    # Handle "Получить карту"
                    if card_img_url.endswith((".gif", ".mp4")):
                        await message.answer_animation(
                            open(card_img_url, "rb"),
                            caption=f"{card_name}\n\n"
                                    f"⚜️ Редкость: {card_rarity}\n"
                                    f"🗡️ Атака: {card_attack}\n"
                                    f"❤️ Здоровье: {card_health}\n\n"
                                    f"💠 Ценность: {card_value} _pts_",
                            parse_mode="Markdown"
                        )
                    else:  # Assume it's an image
                        await message.answer_photo(
                            card_img_url,
                            caption=f"{card_name}\n\n"
                                    f"⚜️ Редкость: {card_rarity}\n"
                                    f"🗡️ Атака: {card_attack}\n"
                                    f"❤️ Здоровье: {card_health}\n\n"
                                    f"💠 Ценность: {card_value} _pts_",
                            parse_mode="Markdown"
                        )

                else:
                    # Handle "Получить карту"
                    if card_img_url.endswith((".gif", ".mp4")):

                        осколки = user_data.get("осколки",0)
                        osk_added = random.randint(40,51)

                        db.users.update_one({"user_id":user_id},{"$set": {"осколки":осколки+osk_added,"seasonal_points":seasonal_points+card_value, "coins":coins+card_value}})

                        await message.answer_animation(
                            open(card_img_url, "rb"),
                            caption=f"🧩🃏 Вау, [{nickname}](tg://user?id={user_id}), попалась мифическая повторка! Тебе будут начислены очки за карту, а также осколки\n\n"
                                    f"⛩️ +{card_value} _pts_\n"
                                    f"🀄️ +{osk_added} _осколков_\n\n"
                                    f"💠 Всего очков: {seasonal_points+card_value} pts",
                            parse_mode="Markdown"
                        )

                    elif card_rarity == "Легендарная":

                        осколки = user_data.get("осколки",0)
                        osk_added = random.randint(10,21)

                        db.users.update_one({"user_id":user_id},{"$set": {"осколки":осколки+osk_added,"seasonal_points":seasonal_points+card_value, "coins":coins+card_value}})

                        await message.answer_photo(
                            card_img_url,
                            caption=f"🩸🃏 Ого, [{nickname}](tg://user?id={user_id}), попалась легендарная повторка! Тебе будут начислены очки за карту, а также осколки\n\n"
                                    f"⛩️ +{card_value} _pts_\n"
                                    f"🀄️ +{osk_added} _осколков_\n\n"
                                    f"💠 Всего очков: {seasonal_points+card_value} pts",
                            parse_mode="Markdown"
                        )

                    else:  # Assume it's an image

                        обычные = user_data.get("обычные")
                        редкие = user_data.get("редкие")
                        эпические = user_data.get("эпические")

                        if card_rarity == "Обычная":
                            db.users.update_one({"user_id":user_id},{"$set":{"обычные":обычные+1}})
                        elif card_rarity == "Редкая":
                            db.users.update_one({"user_id":user_id},{"$set":{"редкие":редкие+1}})
                        else:
                            db.users.update_one({"user_id":user_id},{"$set":{"эпические":эпические+1}})

                        db.users.update_one({"user_id":user_id},{"$set": {"seasonal_points":seasonal_points+card_value, "coins":coins+card_value}})

                        await message.answer_photo(
                            card_img_url,
                            caption=f"🃏[{nickname}](tg://user?id={user_id}), попалась повторка, тебе будут начислены только очки за карту\n\n"
                                    f"⛩️ +{card_value} _pts_\n\n"
                                    f"💠 Всего очков: {seasonal_points+card_value} pts",
                            parse_mode="Markdown"
                        )
            else: 
                await message.answer("❌ Пользователь не найден.")
        else: 
            await message.answer(
                f"🃏🙅‍♂ [{nickname}](tg://user?id={user_id}), получать карточки можно раз в 4 часа. Приходи через:\n"
                f"➖➖➖➖➖➖\n"
                f"⏳ {remaining_hours}ч. {remaining_minutes}м. {remaining_seconds}с",
                parse_mode="Markdown"
            )

    elif "мои карты" in user_input:

        cards_count = casual_cards+rare_cards+epic_cards+legendary_cards+mythic_cards
            
        if cards_count == 0:
                    
            await message.answer(f"🃏🙆 [{nickname}](tg://user?id={user_id}), на данный момент у тебя нет карт", parse_mode="Markdown")

        else: 
            keyboard_cards = InlineKeyboardMarkup(row_width=1)
                
            keyboard_cards.add(
                InlineKeyboardButton(text=f"⚡️ Обычные - {casual_cards}/{maximum_casual}", callback_data="show_casual"),
                InlineKeyboardButton(text=f"✨ Редкие - {rare_cards}/{maximum_rare}", callback_data="show_rare"),
                InlineKeyboardButton(text=f"🐉 Эпические - {epic_cards}/{maximum_epic}", callback_data="show_epic"),
                InlineKeyboardButton(text=f"🩸 Легендарные - {legendary_cards}/{maximum_legendary}", callback_data="show_legendary"),
                InlineKeyboardButton(text=f"🧩 Мифические - {mythic_cards}/{maximum_mythic}", callback_data="show_mythic"),
                InlineKeyboardButton(text=f"⚛️ Все карты - {card_count}/{maximum[0]}", callback_data="show_all"),
                InlineKeyboardButton(text=f"🪬 LIMITED - 0", callback_data="show_limited"),
            )
                    
            # Handle "Мои карты"
            await message.answer(
                f"💬 [{nickname}](tg://user?id={user_id}), какие карты хочешь просмотреть?",
                reply_markup=keyboard_cards, 
                parse_mode="Markdown"
            )     

    elif "меню" in user_input:
        # Handle "Меню"
        
        keyboard = InlineKeyboardMarkup(row_width=2)

        # First row
        keyboard.add(
            InlineKeyboardButton(text="🔑 Pass", callback_data="pass"),
            InlineKeyboardButton(text="🏆 Рейтинг", callback_data="rating"),
        )

        # Second row
        keyboard.add(
            InlineKeyboardButton(text="🔮 Магазин", callback_data="shop"),
            InlineKeyboardButton(text="♻️ Крафт", callback_data="craft")
        )

        # Third row
        keyboard.add(
            InlineKeyboardButton(text="⛺️ Кланы", callback_data="clans"),
            InlineKeyboardButton(text="🏟 Арена", callback_data="arena")
        )

        # Fourth row
        keyboard.add(
            InlineKeyboardButton(text="🌙 Задания", callback_data="tasks"),
            InlineKeyboardButton(text="🔗 Рефералка", callback_data="referral")
        )
        
        # Fifth row
        
        keyboard.add(
            InlineKeyboardButton(text="🗺️ Сменить вселенную", callback_data="change_universe")   
        )
        
        keyboard.add(
            InlineKeyboardButton(text="🎁 Бонусы за Крутки", callback_data="spin_bonuses")
        )
        
        universe_cut = universe.split(" ", 1)[1] if universe != "Не выбрана" else universe
        
        cards_count = casual_cards+rare_cards+epic_cards+legendary_cards+mythic_cards


        await message.answer(
            f"👤 Ник: [{nickname}](tg://user?id={user_id}) \n"
            f"🗺️ Вселенная: {universe_cut} \n"
            f"🃏 Всего карт: {cards_count} из {maximum[0]}\n"
            f"🎖️ Сезонные очки: {seasonal_points} _pts_ \n"
            f"💰 Коины: {coins} 🪙", 
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    elif "настройки" in user_input:
        # Handle "Настройки"
        
        if player_status > 0:
            
            await message.answer(
            f"🪪 Твой ник: {nickname} \n"
            f"🆔 Твой айди: `{user_id}` \n"
            f"🥡 Количество круток: {spin_chances} \n"
            f"🗓 Регистрация: {register_date} \n \n"
            f"📝 Помощь \n"
            f"➢ Изменить ник можно командой \n"
            f"\"`Сменить ник [ник]`\"\n"            
            f"➢ Отключить уведомления можно командой \n"
            f"`Отключить уведомления [карты/арена/босс]`\n"            
            f"➢ Включить уведомления можно командой \n"
            f"`Включить уведомления [карты/арена/босс]`",
            
            parse_mode="Markdown"  
            
            )
            
        else: 
            
            await message.answer(
            f"🪪 Твой ник: {nickname} \n"
            f"🆔 Твой айди: `{user_id}` \n"
            f"🥡 Количество круток: {spin_chances} \n"
            f"🗓 Регистрация: {register_date} \n \n"
            f"📝 Помощь \n ➢ Изменить ник можно командой \n"
            f"\"`Сменить ник [ник]`\"",
            parse_mode="Markdown"  
            
            )
 
    elif "админ панель" in user_input:

        admin_data = db.admins.find_one({"user_id":user_id})
        admins = db.admins.find()
        admin_role = admin_data.get("role")
        
        if not admin_data:
            await message.answer(f"🚫 [{nickname}](tg://user?id={user_id}), вы не являетесь администратором бота.", parse_mode="Markdown")

        else: 

            keyboard = ReplyKeyboardMarkup(row_width=3)

            if admin_role == "limited":
                
                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки", callback_data="admin_spins"),
                    KeyboardButton(text="🔑 Выдать пасс", callback_data="admin_pass"),
                    KeyboardButton(text="✍️ Написать сообщение владельцу", callback_data="admin_message")
                )

                keyboard.add(
                    KeyboardButton(text="⬅️ Назад", callback_data="back"),
                    KeyboardButton(text="🍃 Уволиться", callback_data="admin_retire")
                )

                await message.answer(
                    f"👋 Привет, [{nickname}](tg://user?id={user_id}), ты являешься лимитированный администратором.\n \n"
                    f"✅ Тебе доступны следующие функции:\n \n"
                    f"🔹 `Выдать крутки`\n"
                    f"🔹 `Выдать пасс`\n\n"
                    f"❌ Тебе не доступны следующие функции:\n \n"
                    f"🔹 `Выдать себе крутки`\n"
                    f"🔹 `Выдать себе пасс`\n"
                    f"🔹 `Промокоды`\n"
                    f"🔹 `Пользователи`\n\n"
                    f"🗒 Ты можешь уволиться в любое время нажав на кнопку, или написав в чат: `Уволиться`\n"
                    f"😊 _Желаю тебе хорошего настроения_ - [Владелец бота](https://t.me/donshirley)",
                    parse_mode="Markdown", 
                    reply_markup=keyboard
                )
            
            elif admin_role == "advanced":

                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки", callback_data="admin_spins"),
                    KeyboardButton(text="🔑 Выдать пасс", callback_data="admin_pass"),
                    KeyboardButton(text="✍️ Написать сообщение владельцу", callback_data="admin_message")
                )

                keyboard.add(
                    KeyboardButton(text="👮 Администраторы", callback_data="admin_admins"),
                )

                keyboard.add(
                    KeyboardButton(text="💬 Промокоды", callback_data="admin_promo"),
                    KeyboardButton(text="🌀 Выдать себе крутки", callback_data="admin_selfspins"),
                    KeyboardButton(text="🔑 Выдать себе пасс", callback_data="admin_selfpass")
                )

                keyboard.add(
                    KeyboardButton(text="😐 Пользователи", callback_data="admin_users"),
                )

                keyboard.add(
                    KeyboardButton(text="⬅️ Назад", callback_data="back"),
                    KeyboardButton(text="🍃 Уволиться", callback_data="admin_retire")
                )

                await message.answer(
                    f"👋 Привет, [{nickname}](tg://user?id={user_id}), ты являешься лимитированный администратором.\n \n"
                    f"✅ Тебе доступны продвинутые функции:\n \n"
                    f"🔹 `Выдать себе крутки`\n"
                    f"🔹 `Выдать себе пасс`\n"
                    f"🔹 `Выдать крутки`\n"
                    f"🔹 `Выдать пасс`\n"
                    f"🔹 `Промокоды`\n"
                    f"🔹 `Пользователи`\n"
                    f"🔹 `Администраторы (Просмотр администраторов и владельца бота)` \n\n"
                    f"❌ Тебе не доступны следующие функции:\n \n"
                    f"🔹 `Администраторы (добавление администраторов)`\n"
                    f"🔹 `Ивенты (мифический день, босс, новый сезон, летние и зимние ивенты)`\n\n"
                    f"🗒 Ты можешь уволиться в любое время нажав на кнопку, или написав в чат: `Уволиться`\n"
                    f"😊 _Желаю тебе хорошего настроения_ - [Владелец бота](https://t.me/donshirley)",
                    parse_mode="Markdown", 
                    reply_markup=keyboard
                )

            elif admin_role == "owner":

                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки", callback_data="admin_spins"),
                    KeyboardButton(text="🔑 Выдать пасс", callback_data="admin_pass"),
                )

                keyboard.add(
                    KeyboardButton(text="👮 Администраторы", callback_data="admin_admins"),
                )

                keyboard.add(
                    KeyboardButton(text="💬 Промокоды", callback_data="admin_promo"),
                    KeyboardButton(text="🌀 Выдать себе крутки", callback_data="admin_selfspins"),
                    KeyboardButton(text="🔑 Выдать себе пасс", callback_data="admin_selfpass")
                )

                keyboard.add(
                    KeyboardButton(text="😐 Пользователи", callback_data="admin_promo"),
                )

                keyboard.add(
                    KeyboardButton(text="🔄 Обновиться", callback_data="admin_update"),
                    KeyboardButton(text="🔴 Выключить бота", callback_data="admin_stop"),
                    KeyboardButton(text="🎆 Ивенты", callback_data="admin_events")
                )

                keyboard.add(
                    KeyboardButton(text="⬅️ Назад", callback_data="back"),
                    KeyboardButton(text="💹 Статистика", callback_data="admin_stats")
                )


                await message.answer(
                    f"👋 Привет, [{nickname}](tg://user?id={user_id}), ты являешься владельцем бота.\n \n"
                    f"✅ Тебе доступны все функции:\n \n"
                    f"🔹 `Выдать себе крутки`"
                    f"🔹 `Выдать себе пасс`\n"
                    f"🔹 `Выдать крутки`\n"
                    f"🔹 `Выдать пасс`\n"
                    f"🔹 `Промокоды`\n"
                    f"🔹 `Пользователи`\n"
                    f"🔹 `Администраторы (Просмотр администраторов и владельца бота)`\n"
                    f"🔹 `Администраторы (добавление администраторов)`\n"
                    f"🔹 `Ивенты (мифический день, босс, новый сезон, летние и зимние ивенты)`\n"
                    f"🔹 `Статистика`\n"
                    f"🔹 `Обновиться`\n"
                    f"🔹 `Выключить бота`",
                    parse_mode="Markdown", 
                    reply_markup=keyboard
                )

    elif "назад" in user_input:
        await message.answer("👋", reply_markup=get_main_keyboard(user_id))

    # else:
    #     # Unknown command, ignore or send a generic response
    #     await message.answer("❓ Неизвестная команда. Пожалуйста, выберите доступный вариант из меню.")

universes = {        
        "🪸 Ван пис":"onepiece_data",
        "🍀 Чёрный клевер":"blackclever_data",
        "🗡 Блич":"bleach_data",
        "🍥 Наруто":"naruto_data",
        "🎩 ДжоДжо":"jojo_data",
        "🐜 Хантер × Хантер":"hunterxhunter_data",
        "🥀 Токийский Гуль":"tokyog_data",
        "👊 Ванпанчмен":"onepunchman_data",
        "👺 Истребитель демонов":"demonslayer_data",
        "🪚 Человек бензопила":"chainsawman_data",
        "🍎 Повесть о конце света":"judgedaynotice_data",
        "⚽️ Синяя тюрьма":"bluelock_data",
        "🪄 Магическая битва":"magicfight_data",
        "🧤 Моя геройская академия":"myheroacademy_data",
        "🐷 Семь смертных грехов":"sevensins_data",
        "⚔️ Берсерк":"berserk_data",
        "🩻 Атака титанов":"titanattack_data",
        "📓 Тетрадь смерти":"deathnote_data",
        "🧚 Хвост феи":"fairytail_data",
        "☀️ Сага о Винланде":"winlandsaga_data",
        "⏱️ Токийские мстители":"tokyoavengers_data",
        "🔮 Моб Психо 100":"mobpsycho100_data",
        "⚾️ Покемон":"pokemon_data",
        "☄️ Драгонболл":"dragonball_data",
        "♟ Сололевелинг":"sololevelling_data"
    }

@rate_limit(3)
@dp.callback_query_handler(lambda c: c.data in ["pass", "rating", "shop", "craft", "arena", "clans", "tasks", "referral", "change_universe", "spin_bonuses"])
async def process_callback(callback_query: types.CallbackQuery):
    action = callback_query.data

    if action == "pass":
        # Acknowledge the callback
        await callback_query.answer()

        # Create the keyboard with the payment link button
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(text="🔑 Купить Aniverse pass", callback_data = "payment_page_aniverse_aniverse_pass")
        )
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
        )

        # Send the message with the button
        await callback_query.message.edit_text(
            f"🔓 Что даст тебе Aniverse pass? \n\n"
            f"⛺️ Возможность создать свой собственный клан \n"
            f"⌛️ Возможность получать карточки каждые 3 часа вместо 4 \n"
            f"🏟 Возможность сражаться на арене каждый час вместо 2 \n"
            f"🕒 Уведомления об окончании времени ожидания карт и арены \n"
            f"👾 Уведомления об окончании времени сражения с боссом \n"
            f"🃏 Повышенная вероятность выпадения легендарных, эпических и мифических карт \n"
            f"👤 Возможность использовать смайлики в никнейме \n"
            f"🥡 Получишь +3 крутки \n"
            f"🗓️ Срок действия 30 дней \n \n"
            f"🔑 Aniverse pass - 159 рублей ",
            
            parse_mode="Markdown",
            reply_markup=keyboard
        )
         
    elif action == "rating":
        await callback_query.answer("Вы выбрали Рейтинг. Этот режим в процессе разработки. Вернитесь позже :(")
    elif action == "shop":
        await callback_query.answer("Вы выбрали Магазин. Этот режим в процессе разработки. Вернитесь позже :(")
    elif action == "craft":
        user_id = callback_query.from_user.id
        user_data = db.users.find_one({"user_id":user_id})

        if not user_data:
            await callback_query.message.answer("❌ Пользователь не найден.")

        nickname = user_data.get("nickname", "Гость")
        обычные = user_data.get("обычные", 0)
        редкие = user_data.get("редкие", 0)
        эпические = user_data.get("эпические", 0)
        осколки = user_data.get("осколки",0)

        craftboard = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(text="Скрафтить из ⚡️", callback_data="craft_casual"),
            InlineKeyboardButton(text="Скрафтить из ✨", callback_data="craft_rare"),
            InlineKeyboardButton(text="Скрафтить из 🐉", callback_data="craft_epic"),
            InlineKeyboardButton(text="Скрафтить из 🀄️", callback_data="craft_osk"),
        )

        craftboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
        )

        await callback_query.message.edit_text(
            f"🍙 [{nickname}](tg://user?id={user_id}), ты можешь скрафтить попытки из повторок и осколков\n\n"
            f"🌀 Твои повторки и осколки\n"
            f"┏⚡️ Обычные - {обычные}\n"
            f"┣✨ Редкие - {редкие}\n"
            f"┣🐉 Эпические - {эпические}\n"
            f"┗🀄️ Осколки - {осколки}\n\n"
            f"🍡 Стоимость крафтов\n"
            f"╔10 ⚡️ карт ➠ 1 попытка\n"
            f"╠10 ✨ карт ➠ 2 попытки\n"
            f"╠10 🐉 карт ➠ 4 попытки\n"
            f"╚10 🀄️ оск. ➠ 1 попытка\n\n"
            f"🛢️ Чтобы скрафтить сразу из всех материалов, пиши команду \"`Крафт вся [осколки/обычные/редкие/эпические]`\"",
            parse_mode="Markdown",
            reply_markup=craftboard
        )
    
    elif action == "arena":
        await callback_query.answer("Вы выбрали Арена. Этот режим в процессе разработки. Вернитесь позже :(")
    elif action == "clans":
        await callback_query.answer("Вы выбрали Кланы. Этот режим в процессе разработки. Вернитесь позже :(")
    elif action == "tasks":
        await callback_query.answer("Вы выбрали Задания. Этот режим в процессе разработки. Вернитесь позже :(")
    elif action == "referral":
        
        user_id = callback_query.from_user.id
        
        # Fetch user data
        user_data = db.users.find_one({"user_id": user_id})
        referral_count = user_data.get("referral_count", 0)
        ref_spins = user_data.get("ref_spins", 0)
        referral_link = user_data.get("referral_link", 0)
        nickname = user_data.get("nickname", "Гость")
        
        await callback_query.message.answer(
            f"🔗 [{nickname}](tg://user?id={user_id}), приводи друзей в игру по своей ссылке и получай за это приятные бонусы \n\n"
            f"🌅 За каждых трёх приведённых друзей ты получишь 1 попытку \n\n"
            f"🍙 Привёл игроков: {referral_count}\n"
            f"🪄 Получил попыток: {ref_spins}\n"
            f"⌛️ До обновления: ✅\n"
            f"🤝 Твоя ссылка: `{referral_link}` \n\n"
            f"📬 Такой возможностью можно воспользоваться не больше одного раза в сутки",
            parse_mode = "Markdown"
        )        
    elif action == "change_universe":
        await callback_query.answer("Вы выбрали Сменить вселенную. Этот режим в процессе разработки. Вернитесь позже :(")
    elif action == "spin_bonuses":
        # Handle spin bonuses
        user_id = callback_query.from_user.id

        # Fetch user data
        user_data = db.users.find_one({"user_id": user_id})
        if not user_data:
            await callback_query.answer("❌ Пользователь не найден.")
            return

        total_spins = user_data.get("spins", 0)

        # Define the thresholds and rewards
        thresholds = [
            {"threshold": 10, "reward_spins": 5, "reward_осколки": 0},
            {"threshold": 50, "reward_spins": 10, "reward_осколки": 0},
            {"threshold": 100, "reward_spins": 15, "reward_осколки": 0},
            {"threshold": 350, "reward_spins": 20, "reward_осколки": 50},
            {"threshold": 500, "reward_spins": 50, "reward_осколки": 300},
            {"threshold": 1000, "reward_spins": 100, "reward_осколки": 1000},
            {"threshold": 5000, "reward_spins": 300, "reward_осколки": 5000},
        ]

        # Build the message
        rewards_message = f"💖 {user_data.get('nickname', 'гость')}, получай карты и получай за это награды.\n\n"

        for entry in thresholds:
            threshold = entry["threshold"]
            reward_spins = entry["reward_spins"]
            reward_осколки = entry["reward_осколки"]

            if total_spins >= threshold:
                rewards_message += f"✅ Получено {total_spins} из {threshold}\n"
            else:
                rewards_message += f"❌ Получено {total_spins} из {threshold}\n"

            rewards_message += f"🫀 Награда: {reward_spins} 🃏"
            if reward_осколки > 0:
                rewards_message += f" + {reward_осколки} 🀄️"
            rewards_message += "\n\n"

        # Send the message
        await callback_query.message.edit_text(
            rewards_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🎁 Забрать награду", callback_data="claim_spins"),
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")
            )
        )
        

@dp.callback_query_handler(lambda c: c.data.startswith("craft_"))
async def use_craft(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = db.users.find_one({"user_id":user_id})

    nickname = user_data.get("nickname", "Гость")
    обычные = user_data.get("обычные", 0)
    редкие = user_data.get("редкие", 0)
    эпические = user_data.get("эпические", 0)
    осколки = user_data.get("осколки",0)
    spin_chances = user_data.get("spin_chances", 0)
    action = callback_query.data.split("_")[1]

    if not user_data:
        await callback_query.message.answer("❌ Пользователь не найден.")

    else:
        if action == "casual":
            if обычные>=10:
                db.users.update_one({"user_id":user_id},{"$set":{"обычные":обычные-10,"spin_chances":spin_chances+1}})
                await callback_query.message.answer(
                    f"♻️🥡 [{nickname}](tg://user?id={user_id}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 ⚡️ карт ➠ 1 попытка_\n",
                    parse_mode="Markdown"
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)
            
        elif action == "rare":
            if редкие>=10:
                db.users.update_one({"user_id":user_id},{"$set":{"редкие":редкие-10,"spin_chances":spin_chances+2}})
                await callback_query.message.answer(
                    f"♻️🥡 [{nickname}](tg://user?id={user_id}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 ✨ карт ➠ 2 попытка_\n",
                    parse_mode="Markdown"
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)

        elif action == "epic":
            if эпические>=10:
                db.users.update_one({"user_id":user_id},{"$set":{"эпические":эпические-10,"spin_chances":spin_chances+4}})
                await callback_query.message.answer(
                    f"♻️🥡 [{nickname}](tg://user?id={user_id}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 🐉 карт ➠ 4 попытка_\n",
                    parse_mode="Markdown"
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)

        elif action == "osk":
            if осколки>=10:
                db.users.update_one({"user_id":user_id},{"$set":{"осколки":осколки-10,"spin_chances":spin_chances+1}})
                await callback_query.message.answer(
                    f"♻️🥡 [{nickname}](tg://user?id={user_id}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 🀄️ карт ➠ 1 попытка_\n",
                    parse_mode="Markdown"
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)

    
@rate_limit(5)
@dp.callback_query_handler(lambda c: c.data.startswith("claim_spins"))
async def claim_spins(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Fetch user data
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data:
        await callback_query.answer("❌ Пользователь не найден.")
        return

    # Get user details with default values to avoid KeyError
    nickname = user_data.get("nickname", "Гость")
    total_spins = user_data.get("spins", 0)
    spins = user_data.get("spin_chances", 0)
    осколки = user_data.get("осколки", 0)
    redeemed = user_data.get("redeemed", [])  # Initialize as an empty list if None

    # Define the thresholds and rewards
    thresholds = [
        {"threshold": 10, "reward_spins": 5, "reward_осколки": 0},
        {"threshold": 50, "reward_spins": 10, "reward_осколки": 0},
        {"threshold": 100, "reward_spins": 15, "reward_осколки": 0},
        {"threshold": 350, "reward_spins": 20, "reward_осколки": 50},
        {"threshold": 500, "reward_spins": 50, "reward_осколки": 300},
        {"threshold": 1000, "reward_spins": 100, "reward_осколки": 1000},
        {"threshold": 5000, "reward_spins": 300, "reward_осколки": 5000},
    ]

    # Iterate through thresholds to check eligibility

    for entry in thresholds:
        threshold = entry["threshold"]
        reward_spins = entry["reward_spins"]
        reward_осколки = entry["reward_осколки"]

        if total_spins >= threshold and threshold not in redeemed:
            # Mark threshold as redeemed
            redeemed.append(threshold)
            
            # Update user data in the database
            db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "осколки": осколки + reward_осколки,
                        "spin_chances": spins + reward_spins,
                        "redeemed": redeemed,
                    }
                },
            )

            # Send success message
            message = (
                f"🧸 [{nickname}](tg://user?id={user_id}), ты успешно выполнил задание. Тебе начислено:\n"
                f"➖➖➖➖➖➖\n"
                f"{reward_spins} 🃏 круток"
                if reward_осколки == 0
                else f"🧸 [{nickname}](tg://user?id={user_id}), ты успешно выполнил задание. Тебе начислено:\n"
                f"➖➖➖➖➖➖\n"
                f"{reward_spins} 🃏 круток и {reward_осколки} 🀄️ осколков"
            )
            await callback_query.message.answer(message)
            

        elif total_spins >= threshold and threshold in redeemed:
            # Reward already claimed
            await callback_query.answer(f"⭐️ {nickname}, ты уже получил награду за выполненные задания.")
            

       
@rate_limit(5) 
@dp.callback_query_handler(lambda c: c.data.startswith("payment_page_"))
async def payment_page_aniverse(callback_query: types.CallbackQuery):
    """
    Handle the payment page for the user.
    The type of purchase and its price will be dynamically fetched from the database based on callback data.
    """
    # Acknowledge the callback
    await callback_query.answer()
        
    keys = InlineKeyboardMarkup(row_width=2)

    keys.add(
            InlineKeyboardButton(text="🛒 Оплатить", callback_data="alternative_payment_aniverse_aniverse_pass"),
            InlineKeyboardButton(text="✅ Я оплатил", callback_data="payment_completed")
    )
        
    keys.add(
            InlineKeyboardButton(text="✏️ Другие Способы", callback_data="alternative_payment_aniverse_aniverse_pass")  
    )
        
    keys.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_aniverse")
    )
    
    await callback_query.message.edit_text(
        f"🧾 Покупка Aniverse pass\n"
        f"💵 Стоимость: 159 рублей \n"
        f"➖➖➖➖➖➖\n"
        f"‼️ `После оплаты нажми кнопку \"я оплатил\"`.\n\n"
        f"💬 `Возникли сложности с донатом? Пиши сюда - ` @donshirley \n"
        f"➖➖➖➖➖➖\n"
        f"[Пользовательское соглашение](https://telegra.ph/Polzovatelskoe-soglashenie-06-01-5)",
        parse_mode="Markdown",
        reply_markup=keys,
        disable_web_page_preview=True
    )


@rate_limit(5)
@dp.callback_query_handler(lambda c: c.data.startswith("alternative_payment_"))
async def alternative_payment(callback_query: types.CallbackQuery):

    # Acknowledge the callback
    await callback_query.answer()
    
    user_id = callback_query.from_user.id
    
    purchase_type = callback_query.data.split("_", 3)[3] 
    
    # Create the keyboard with the payment link button
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="📥 Отправить чек", url="t.me/donshirley")
    )
    keyboard.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_paymentaniverse")
    )


    # Fetch the price of the selected purchase from the database
    pricing_data = db.pricing.find_one({"type": purchase_type})  # Assuming pricing data is stored in the "pricing" collection

    capital_name = (purchase_type.capitalize().split("_"))[0]+" "+(purchase_type.capitalize().split("_"))[1]

    # Get the price from the pricing data
    price = pricing_data.get("price", 0)

    await callback_query.message.edit_text(
        f"🧾 Покупка {capital_name}\n"
        f"💵 Стоимость: {price} рублей \n"
        f"➖➖➖➖➖➖\n"
        
        f"🛂 Способы оплаты \n\n"
        f"💳 Сбербанк карта:\n"
        f"⇨ `4279 3806 7943 8913`\n"
        f"💰 Тинькофф карта:\n"
        f"⇨ `2200 7008 8751 1391`\n"
        f"🥝 Оплата на киви:\n"
        f"⇨ [Жми на эту ссылку](https://my.qiwi.com/Ashtar-AmkT7jgxyM)\n"
        f"🗾 Оплата с зарубежных карт:\n"
        f"⇨ [Жми на эту ссылку](https://boosty.to/aniverse/donate)\n"
        f"➖➖➖➖➖➖\n"
        f"‼️ `После оплаты отправь чек и свой ID по ссылке ниже` \n"
        f"🆔 Твой айди: `{user_id}`\n\n"
        
        f"[Пользовательское соглашение](https://telegra.ph/Polzovatelskoe-soglashenie-06-01-5)\n",
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    
@rate_limit(0.5)
@dp.callback_query_handler(lambda c: c.data.startwith("admin"))
async def admin_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.answer()

    action = callback_query.split("_")[1]

    if action == "update":

        user_id = callback_query.from_user.id
        admin_data = db.admins.find_one({"user_id":user_id})

        # Check if the user is authorized
        if not admin_data or admin_data.get("role") != "owner":
            await callback_query.answer("🚫 Вы не авторизованы или не являетесь администратором.")
            return

        await callback_query.answer("🔄 Обновление бота... Пожалуйста подождите.")

        # Pull latest changes from GitHub
        try:
            result = subprocess.run(["git", "pull"], capture_output=True, text=True, check=True)
            git_output = result.stdout
        except subprocess.CalledProcessError as e:
            await callback_query.answer(f"❌ Не удалось получить обновления с GitHub:\n{e.stderr}")
            return

        await callback_query.answer(f"✅ Обновления синхронизированы:\n`\n{git_output}\n`", parse_mode="Markdown")

        # Restart the bot
        if git_output != "Already up to date.":
            try:
                await callback_query.answer("♻️ Перезапускаю бота...")
                os.execl(sys.executable, sys.executable, *sys.argv)
            except Exception as e:
                await callback_query.answer(f"❌ Не удалось перезапустить бота:\n{e}")

# Run the Bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
