from rate_limit import rate_limit
from aiogram import types
from db import db

@rate_limit(5)
async def claim_spins(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Fetch user data
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data:
        await callback_query.answer("❌ Пользователь не найден.")
        return

    # Get user details with default values to avoid KeyError
    nickname = user_data.get("nickname", "Гость")
    username = user_data.get("username")
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
                f"🧸 [{nickname}](https://t.me/{username}), ты успешно выполнил задание. Тебе начислено:\n"
                f"➖➖➖➖➖➖\n"
                f"{reward_spins} 🃏 круток"
                if reward_осколки == 0
                else f"🧸 [{nickname}](https://t.me/{username}), ты успешно выполнил задание. Тебе начислено:\n"
                f"➖➖➖➖➖➖\n"
                f"{reward_spins} 🃏 круток и {reward_осколки} 🀄️ осколков",
            )
            await callback_query.message.answer(message,disable_web_page_preview=True)
            

        elif total_spins >= threshold and threshold in redeemed:
            # Reward already claimed
            await callback_query.answer(f"⭐️ {nickname}, ты уже получил награду за выполненные задания.")
