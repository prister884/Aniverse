from rate_limit import rate_limit
from aiogram import types
from db import db
from handlers.menu import handle_menu

@rate_limit(0.5)
async def craft_all(message: types.Message):

    user_id = message.from_user.id
    user_data = db.users.find_one({"user_id":user_id})

    nickname = user_data.get("nickname", "Гость")
    username = user_data.get("username")

    осколки = user_data.get("осколки", 0)
    обычные = user_data.get("обычные", 0)
    редкие = user_data.get("редкие", 0)
    эпические = user_data.get("эпические", 0)

    if message.text.lower().startswith("крафт вся"):
        parts = message.text.split(maxsplit=2)

        if len(parts) < 3 or len(parts) > 3:

            await message.answer(
                f"ℹ️ [{nickname}](https://t.me/{username}), чтобы скрафтить крутки сразу из всех материалов, пиши команду \"крафт вся [осколки/обычные/редкие/эпические]\". \n\n"
                f"🧤 Примеры команд:\n"
                f"➤ `Крафт вся осколки`\n"
                f"➤ `Крафт вся обычные`\n"
                f"➤ `Крафт вся редкие`\n"
                f"➤ `Крафт вся эпические`\n",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        
        else: 

            emojis = {
                "осколки": "🀄️",
                "обычные": "⚡",
                "редкие": "✨",
                "эпические": "🐉",
            }

            craft_type = "повторок"

            if parts[2] == "осколки": 
                craft_type = "осколков"
                craft = "осколки"
                craft_amount = (осколки//10)*1
            elif parts[2] == "обычные":
                craft_amount = (обычные//10)*1
                craft = "обычные"
            elif parts[2] == "редкие":
                craft_amount = (редкие//10)*2
                craft = "редкие"
            elif parts[2] == "эпические":
                craft_amount = (эпические//10)*4
                craft = "эпические"
            
            else:
                await message.answer(
                    f"ℹ️ [{nickname}](https://t.me/{username}), чтобы скрафтить крутки сразу из всех материалов, пиши команду \"крафт вся [осколки/обычные/редкие/эпические]\". \n\n"
                    f"🧤 Примеры команд:\n"
                    f"➤ `Крафт вся осколки`\n"
                    f"➤ `Крафт вся обычные`\n"
                    f"➤ `Крафт вся редкие`\n"
                    f"➤ `Крафт вся эпические`\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

            if craft_amount > 0:

                craftable = user_data.get(f"{craft}", 0)

                db.users.update_one(
                    {"user_id": user_id},
                    {"$set":{
                        f"{craft}":craftable-((craftable//10)*10),
                        "spin_chances":user_data.get("spin_chances")+craft_amount
                    }}
                )


                await message.answer(
                    f"♻️🥡 [{nickname}](https://t.me/{username}), крафт прошёл успешно\n"
                    f"➖➖➖➖➖➖\n"
                    f"🧱 Потрачено {craft_type}: {(craftable//10)*10} {emojis[parts[2]]}\n"
                    f"🌌 Получено круток: {craft_amount} 🃏",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            else: 
                await message.answer(
                    f"🌀 [{nickname}](https://t.me/{username}), недостаточно материалов для крафта.",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

    else: await handle_menu(message)

async def use_craft(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = db.users.find_one({"user_id":user_id})

    nickname = user_data.get("nickname", "Гость")
    username = user_data.get("username")
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
                    f"♻️🥡 [{nickname}](https://t.me/{username}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 ⚡️ карт ➠ 1 попытка_\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)
            
        elif action == "rare":
            if редкие>=10:
                db.users.update_one({"user_id":user_id},{"$set":{"редкие":редкие-10,"spin_chances":spin_chances+2}})
                await callback_query.message.answer(
                    f"♻️🥡 [{nickname}](https://t.me/{username}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 ✨ карт ➠ 2 попытка_\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)

        elif action == "epic":
            if эпические>=10:
                db.users.update_one({"user_id":user_id},{"$set":{"эпические":эпические-10,"spin_chances":spin_chances+4}})
                await callback_query.message.answer(
                    f"♻️🥡 [{nickname}](https://t.me/{username}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 🐉 карт ➠ 4 попытка_\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)

        elif action == "osk":
            if осколки>=10:
                db.users.update_one({"user_id":user_id},{"$set":{"осколки":осколки-10,"spin_chances":spin_chances+1}})
                await callback_query.message.answer(
                    f"♻️🥡 [{nickname}](https://t.me/{username}), крафт прошёл успешно:\n"
                    f"➖➖➖➖➖➖\n"
                    f"_10 🀄️ осколков ➠ 1 попытка_\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            else: 
                await callback_query.answer("🌀 Тебе не хватает повторок", show_alert=True)
