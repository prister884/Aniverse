import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from pymongo import MongoClient
from aiogram.utils.exceptions import MessageToDeleteNotFound
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb+srv://abdurazzoqov057:yqW7tgxtYjcROPkM@cluster0.ttusl.mongodb.net/?retryWrites=true&w=majority")
db = client.aniverse_db  # Use your database name

# Bot Token
BOT_TOKEN = "7934666713:AAGzvsNfe8K6BhISbL-fwUDeltItz-v6Gmw"

# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Main Menu Keyboard
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("🥡 Получить карту"),
        KeyboardButton("🃏 Мои карты")
    )
    keyboard.add(
        KeyboardButton("☁ Меню"),
        KeyboardButton("⚙ Настройки")
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
    
# Handle Start Command
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Check if the user exists in MongoDB
    user_data = db.users.find_one({"user_id": user_id})

    if user_data:
        universe = user_data.get("universe")

        # Check universe data if a universe is selected
        verse_data = None
        if universe:
            verse_data = db.universes.find_one({"name": universe})
            maximum_cards = verse_data.get("maximum", 0) if verse_data else 0

        # User exists, greet them
        nickname = user_data.get("nickname", "Гость")
        await message.answer(
            f"👋 [{nickname}](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
            f"🃏 Цель игры в коллекционировании карточек. Собирай карточки и борись за место в топе \n\n"
            f"🌏 Вселенные будут постоянно обновляться и улучшаться",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()  # Display main menu keyboard
        )
    else:
        # Add new user to MongoDB
        db.users.insert_one({
            "user_id": user_id,
            "username": username,
            "nickname": "Гость",
            "universe": "Не выбрана",  # No universe selected yet
            "cards": [],
            "seasonal_points": 0,
            "spin_chances": 1,
            "coins": 0,
            "player_status": 0,  # Indicates the number of days the Aniverse Pass is valid for
            "arena_notif": False,
            "spin_notif": False,
            "boss_notif": False,
            "is_admin": False,
            "register_date": datetime.now().strftime("%d.%m.%Y в %H:%M"),
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



@dp.callback_query_handler(lambda c: c.data == "back_to_welcome")
async def back_to_welcome(callback_query: types.CallbackQuery):
    """
    Handle the "back" button that takes the user back to the welcome screen.
    """
    user_id = callback_query.from_user.id
    
    # Check if the user exists in the database
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data:
        await callback_query.answer("❌ Пожалуйста, сначала введите команду /start.")
        return

    # Send a message to navigate back to the welcome screen
    await callback_query.message.edit_text(
        "👋 Добро пожаловать в Aniverse card! Для начала выбери вселенную.",
        reply_markup=get_welcome_buttons(),  # Show the welcome buttons again
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    
    # Acknowledge the callback to ensure the transition is visible to the user
    await callback_query.answer()




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

# Handle Paginate Universes
@dp.callback_query_handler(lambda c: c.data.startswith("page_"))
async def paginate_universes(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[1])  # Extract page number
    await callback_query.message.edit_text(
        "🌌 Выберите вселенную из списка ниже:",
        reply_markup=get_universe_keyboard(page=page)
    )

@dp.callback_query_handler(lambda c: c.data.startswith("universe_"))
async def select_universe(callback_query: types.CallbackQuery):
    """
    Handle user universe selection and save it to the database.
    """
    user_id = callback_query.from_user.id
    universe_name = callback_query.data.split("_", 1)[1]  # Extract universe name

    # Fetch universe data to get maximum number of cards
    verse_data = db.universes.find_one({"name": universe_name})
    maximum_cards = verse_data.get("maximum", 0) if verse_data else 0

    # Update the user's selected universe and maximum cards in MongoDB
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"universe": universe_name, "maximum_cards": maximum_cards}}
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
        reply_markup=get_main_keyboard()  # Show main keyboard after universe selection
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


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_menu(message: types.Message):
    """
    Handle actions from the reply keyboard menu under the message bar.
    """
    user_id = message.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    nickname = user_data.get("nickname")
    spin_chances = user_data.get("spin_chances", 0)
    universe = user_data.get("universe", "Не выбрана")
    seasonal_points = user_data.get("seasonal_points", 0)
    register_date = user_data.get("register_date")
    player_status = user_data.get("player_status")
    coins = user_data.get("coins")
    maximum = user_data.get("maximum_cards")
    cards = user_data.get("cards", [])
    
    if not user_data:
        await message.answer("❌ Пожалуйста, сначала введите команду /start.")
        return

    # Normalize the text to handle case-insensitive matches
    user_input = message.text.strip().lower()

    if "получить карту" in user_input:
        # Handle "Получить карту"
        await message.answer("✨ Вы нажали на \"`Получить карту`\". Функционал скоро будет добавлен.")
    
    elif "мои карты" in user_input:
        # Handle "Мои карты"
        if not cards:
            await message.answer("🃏 У вас ещё нет карт. Нажмите \"`Получить карту`\", чтобы начать коллекцию.")
        else:
            card_list = "\n".join([f"- {card['name']} ({card['rarity']})" for card in cards])
            await message.answer(f"📜 Ваши карты:\n{card_list}")

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
        
        await message.answer(
            f"👤 Ник: [{nickname}](tg://user?id={user_id}) \n"
            f"🗺️ Вселенная: {universe_cut} \n"
            f"🃏 Всего карт: {len(cards)} из {maximum}\n"
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
            f"`Сменить ник [ник]`\n"            
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
            f"`Сменить ник [ник]`",
            parse_mode="Markdown"  
            
            )
   
    else:
        # Unknown command, ignore or send a generic response
        await message.answer("❓ Неизвестная команда. Пожалуйста, выберите доступный вариант из меню.")


@dp.callback_query_handler(lambda c: c.data in ["pass", "rating", "shop", "craft", "arena", "clans", "tasks", "referral", "change_universe", "spin_bonuses"])
async def process_callback(callback_query: types.CallbackQuery):
    action = callback_query.data

    if action == "pass":
        await callback_query.answer("Вы выбрали Pass.")
    elif action == "rating":
        await callback_query.answer("Вы выбрали Рейтинг.")
    elif action == "shop":
        await callback_query.answer("Вы выбрали Магазин.")
    elif action == "craft":
        await callback_query.answer("Вы выбрали Крафт.")
    elif action == "arena":
        await callback_query.answer("Вы выбрали Арена.")
    elif action == "clans":
        await callback_query.answer("Вы выбрали Кланы.")
    elif action == "tasks":
        await callback_query.answer("Вы выбрали Задания.")
    elif action == "referral":
        await callback_query.answer("Вы выбрали Рефералка.")
    elif action == "change_universe":
        
        # Handle changing the universe with pagination
        user_id = callback_query.from_user.id
        # Get user data from MongoDB
        user_data = db.users.find_one({"user_id": user_id})

        if not user_data:
            await callback_query.answer("Пользователь не найден в базе данных.")
            return

        await callback_query.message.edit_text(
            f"🌌 Выберите вселенную из списка ниже:",
            reply_markup=get_universe_keyboard_change(page=1)
        )

    elif action == "spin_bonuses":
        await callback_query.answer("Вы выбрали Бонусы за Крутки.")

def get_universe_keyboard_change(page=1):
    """
    Generate a paginated inline keyboard for universes from MongoDB.
    """
    universes = db.universes.find()  # Fetch universes from MongoDB
    items_per_page = 7
    skip_items = (page - 1) * items_per_page
    universes = list(universes.skip(skip_items).limit(items_per_page))

    keyboard = InlineKeyboardMarkup(row_width=1)
    for universe in universes:
        keyboard.add(InlineKeyboardButton(universe["name"], callback_data=f"change_universe_{universe['name']}"))

    navigation_buttons = []
    navigation_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu"))
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton("👆", callback_data=f"page_{page - 1}"))
    if len(universes) == items_per_page:
        navigation_buttons.append(InlineKeyboardButton("👇", callback_data=f"page_{page + 1}"))

    if navigation_buttons:
        keyboard.row(*navigation_buttons)


    return keyboard


@dp.callback_query_handler(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: types.CallbackQuery):
    
    user_id = callback_query.from_user.id
    
    user_data = db.users.find_one({"user_id": user_id})
    
    nickname = user_data.get("nickname", "Гость")
    
    spin_chances = user_data.get("spin_chances", 0)
    universe = user_data.get("universe", "Не выбрана")
    seasonal_points = user_data.get("seasonal_points", 0)
    register_date = user_data.get("register_date")
    player_status = user_data.get("player_status")
    coins = user_data.get("coins")
    maximum = user_data.get("maximum_cards")
    cards = user_data.get("cards", [])
    
    # Acknowledge the callback
    await callback_query.answer()

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
        
    universe_cut = universe.split(" ", 1)[1]
        
    await callback_query.message.edit_text(
        f"👤 Ник: [{nickname}](tg://user?id={user_id}) \n"
        f"🗺️ Вселенная: {universe_cut} \n"
        f"🃏 Всего карт: {len(cards)} из {maximum}\n"
        f"🎖️ Сезонные очки: {seasonal_points} _pts_ \n"
        f"💰 Коины: {coins} 🪙", 
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data.startswith("change_universe_"))
async def change_current_universe(callback_query: types.CallbackQuery):
    """ 
    Handle user universe change and save it to the database. 
    """ 
    user_id = callback_query.from_user.id 
    universe_name = callback_query.data.split("_", 1)[1]  # Extract universe name 

    # Acknowledge the callback 
    await callback_query.answer() 

    # Confirm the selection 
    user_data = db.users.find_one({"user_id": user_id}) 
    nickname = user_data.get("nickname", "Гость") 

    # Correct the keyboard and message 
    await callback_query.message.edit_text( 
        f"🌱 [{nickname}](tg://user?id={user_id}), ты можешь сохранить свой прогресс в этой вселенной за 30000 🪙 коинов. \n\n" 
        f"‼️ Или же сменить вселенную бесплатно, но при этом все твои карточки и очки будут обнулены. ", 
        parse_mode="Markdown", 
        reply_markup=confirm_change(callback_query), 
        disable_web_page_preview=True, 
    ) 

def confirm_change(callback_query_input): 
    user_id = callback_query_input.from_user.id 
    universe_name = callback_query_input.data.split("_", 1)[1]  # Extract universe name 

    keyboard = InlineKeyboardMarkup(row_width=2) 
    keyboard.add( 
        InlineKeyboardButton(text="💾 Сохранить", callback_data=f"save_universe_data_{universe_name}"), 
        InlineKeyboardButton(text="♨️ Не сохранять", callback_data=f"reset_universe_data_{universe_name}") 
    ) 
    keyboard.add( 
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_change") 
    ) 
    return keyboard 

@dp.callback_query_handler(lambda c: c.data.startswith("save_universe_data_") or c.data.startswith("reset_universe_data_"))
async def handle_universe_change(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id 
    await callback_query.answer() 

    # Extract universe name from callback data 
    universe_name = callback_query.data.split("_", 2)[2]  # Extract universe name correctly 

    # Fetch user data 
    user_data = db.users.find_one({"user_id": user_id}) 
    if not user_data: 
        await callback_query.answer("❌ Пользователь не найден.") 
        return 

    # Fetch universe data 
    verse_data = db.universes.find_one({"name": universe_name}) 
    if not verse_data: 
        await callback_query.answer("❌ Вселенная не найдена в базе данных.") 
        return 

    # Fetch current universe and its data 
    current_universe = user_data.get("universe") 
    current_cards = user_data.get("cards", []) 
    current_seasonal_points = user_data.get("seasonal_points", 0) 
    current_coins = user_data.get("coins", 0) 

    if callback_query.data.startswith("save_universe_data"): 
        # Save the user's progress in the current universe 
        db.users.update_one( 
            {"user_id": user_id}, 
            { 
                "$set": { 
                    f"saved_data.{current_universe}.cards": current_cards, 
                    f"saved_data.{current_universe}.seasonal_points": current_seasonal_points, 
                    f"saved_data.{current_universe}.coins": current_coins,
                    "universe": universe_name, 
                    "maximum_cards": verse_data.get("maximum", 0), 
                    "cards": current_cards,  # Keep current cards
                    "seasonal_points": current_seasonal_points,  # Keep seasonal points
                    "coins": current_coins  # Keep coins
                } 
            } 
        ) 
        await callback_query.message.edit_text("✅ Ваш прогресс сохранён и вселенная изменена.") 
    elif callback_query.data.startswith("reset_universe_data"): 
        # Reset user data for the new universe 
        db.users.update_one( 
            {"user_id": user_id}, 
            { 
                "$set": { 
                    "universe": universe_name, 
                    "maximum_cards": verse_data.get("maximum", 0), 
                    "cards": [],  # Reset cards
                    "seasonal_points": 0,  # Reset seasonal points
                    "coins": 0  # Reset coins
                } 
            } 
        ) 
@dp.callback_query_handler(lambda c: c.data == "back_to_change")
async def back_to_change(callback_query: types.CallbackQuery):
    """
    Handle the back action to return to the universe selection menu.
    """
    # Acknowledge the callback
    await callback_query.answer()
    
    page = 1

    # Send the updated universe selection menu
    await callback_query.message.edit_text(
        "Выберите вселенную из списка ниже:",
        reply_markup=get_universe_keyboard_change(page=page)
    )


# Run the Bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
