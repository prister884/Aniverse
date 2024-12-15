from rate_limit import rate_limit
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import db

@rate_limit(3)
async def process_callback(callback_query: types.CallbackQuery):
    action = callback_query.data

    if action == "pass":
        # Acknowledge the callback
        await callback_query.answer()

        # Create the keyboard with the payment link button
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(text="🔑 Купить Aniverse pass", callback_data = "payment_page_aniverse_pass")
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
        username = user_data.get("username")
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
            f"🍙 [{nickname}](https://t.me/{username}), ты можешь скрафтить попытки из повторок и осколков\n\n"
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
            reply_markup=craftboard,
            disable_web_page_preview=True
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
        username = user_data.get("username")
        
        await callback_query.message.answer(
            f"🔗 [{nickname}](https://t.me/{username}), приводи друзей в игру по своей ссылке и получай за это приятные бонусы \n\n"
            f"🌅 За каждых трёх приведённых друзей ты получишь 1 попытку \n\n"
            f"🍙 Привёл игроков: {referral_count}\n"
            f"🪄 Получил попыток: {ref_spins}\n"
            f"⌛️ До обновления: ✅\n"
            f"🤝 Твоя ссылка: `{referral_link}` \n\n"
            f"📬 Такой возможностью можно воспользоваться не больше одного раза в сутки",
            parse_mode = "Markdown",
            disable_web_page_preview=True
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
  