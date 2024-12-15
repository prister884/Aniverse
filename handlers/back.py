from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from rate_limit import rate_limit
from db import db
from keyboards.main_keyboard import get_main_keyboard

@rate_limit(1)
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
    username = user_data.get("username")
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
        banned_user = db.banned.find_one({"user_id":user_id})

        if not user_data:
            await callback_query.answer("❌ Пожалуйста, сначала введите команду /start.")
            return

        if not banned_user:

            await callback_query.message.edit_text(
                f"👋 [{nickname}](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
                f"🃏 Цель игры в коллекционировании карточек. Собирай карточки и борись за место в топе \n\n"
                f"🌏 Вселенные будут постоянно обновляться и улучшаться",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(user_id),
                disable_web_page_preview=True  # Display main menu keyboard
            )
        
        else: 

            unban_request = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="Подать заявку на разбан", url="https://t.me/aniverseclone_don"),
                InlineKeyboardButton(text="Разбан без проверки за 555 руб.", callback_data="alternative_payment")
            )

            # Greet the new user
            await callback_query.message.answer(
                f"👋 [Гость](tg://user?id={user_id}), добро пожаловать во вселенную Aniverse card.\n\n"
                f"🃏 К сожалению вы были забанены администраторами бота!\n",
                reply_markup=unban_request,
                parse_mode="Markdown",
                disable_web_page_preview=True  # Disable link preview for greeting message
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
            f"👤 Ник: [{nickname}](https://t.me/{username}) \n"
            f"🗺️ Вселенная: {universe_cut} \n"
            f"🃏 Всего карт: {cards_count} из {maximum[0]}\n"
            f"🎖️ Сезонные очки: {seasonal_points} _pts_ \n"
            f"💰 Коины: {coins} 🪙", 
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

    elif back_type == "paymentaniverse":
        
        # Acknowledge the callback
        await callback_query.answer()
        
        keys = InlineKeyboardMarkup(row_width=2)

        keys.add(
                InlineKeyboardButton(text="🛒 Оплатить", callback_data="alternative_payment_aniverse_aniverse_pass"),
                InlineKeyboardButton(text="✅ Я оплатил", url="t.me/aniverseclone_don")
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
