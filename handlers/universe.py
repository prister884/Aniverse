from rate_limit import rate_limit
from dp import dp
from aiogram import types
from db import db
from keyboards.universe_keyboard import get_universe_keyboard
from keyboards.main_keyboard import get_main_keyboard
from aiogram.utils.exceptions import MessageToDeleteNotFound

@rate_limit(1)
# Handle Choose Universe
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
async def paginate_universes(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[1])  # Extract page number
    await callback_query.message.edit_text(
        "🌌 Выберите вселенную из списка ниже:",
        reply_markup=get_universe_keyboard(page=page)
    )

@rate_limit(1)
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
    username = user_data.get("username")
    user_link = f"[{nickname}](https://t.me/{username})"

    # Correct the keyboard and message
    await callback_query.message.edit_text(
        f"🏔 [{nickname}](https://t.me/{username}), твоя выбранная вселенная: {universe_name}.\n ➖➖➖➖➖➖ \n"
        f"🥡 Чтобы получить карту, напиши команду \"`Получить карту`\".",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
    
    await callback_query.message.answer(
        f"🏔 [{nickname}](https://t.me/{username}), твоя выбранная вселенная: {universe_name}.\n ➖➖➖➖➖➖ \n"
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
