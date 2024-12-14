from rate_limit import rate_limit
from aiogram import types
from db import db
import time
import random
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.admin import admin_message_handler

@rate_limit(0.5)
async def handle_menu(message: types.Message):
    """
    Handle actions from the reply keyboard menu under the message bar.
    """
    user_id = message.from_user.id
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

    casual_cards = len(cards[0])
    rare_cards = len(cards[1])
    epic_cards = len(cards[2])
    legendary_cards = len(cards[3])
    mythic_cards = len(cards[4])
    card_count = casual_cards+rare_cards+epic_cards+legendary_cards+mythic_cards

    
    maximum = verse_data.get("maximum", []) if verse_data else []
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
                            caption=f"🧩🃏 Вау, [{nickname}](https://t.me/{username}), попалась мифическая повторка! Тебе будут начислены очки за карту, а также осколки\n\n"
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
                            caption=f"🩸🃏 Ого, [{nickname}](https://t.me/{username}), попалась легендарная повторка! Тебе будут начислены очки за карту, а также осколки\n\n"
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
                            caption=f"🃏[{nickname}](https://t.me/{username}), попалась повторка, тебе будут начислены только очки за карту\n\n"
                                    f"⛩️ +{card_value} _pts_\n\n"
                                    f"💠 Всего очков: {seasonal_points+card_value} pts",
                            parse_mode="Markdown"
                        )
            else: 
                await message.answer("❌ Пользователь не найден.")
        else: 
            await message.answer(
                f"🃏🙅‍♂ [{nickname}](https://t.me/{username}), получать карточки можно раз в 4 часа. Приходи через:\n"
                f"➖➖➖➖➖➖\n"
                f"⏳ {remaining_hours}ч. {remaining_minutes}м. {remaining_seconds}с",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

    elif "мои карты" in user_input:

        cards_count = casual_cards+rare_cards+epic_cards+legendary_cards+mythic_cards
            
        if cards_count == 0:
                    
            await message.answer(f"🃏🙆 [{nickname}](https://t.me/{username}), на данный момент у тебя нет карт", parse_mode="Markdown",disable_web_page_preview=True)

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
                f"💬 [{nickname}](https://t.me/{username}), какие карты хочешь просмотреть?",
                reply_markup=keyboard_cards, 
                parse_mode="Markdown",
                disable_web_page_preview=True
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
            f"👤 Ник: [{nickname}](https://t.me/{username}) \n"
            f"🗺️ Вселенная: {universe_cut} \n"
            f"🃏 Всего карт: {cards_count} из {maximum[0]}\n"
            f"🎖️ Сезонные очки: {seasonal_points} _pts_ \n"
            f"💰 Коины: {coins} 🪙", 
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

    elif "настройки" in user_input:

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
            await message.answer(f"🚫 [{nickname}](https://t.me/{username}), вы не являетесь администратором бота.", parse_mode="Markdown",disable_web_page_preview=True)

        else: 

            keyboard = ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)

            if admin_role == "limited":
                
                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки"),
                    KeyboardButton(text="🔑 Выдать пасс"),
                    KeyboardButton(text="✍️ Написать сообщение владельцу")
                )

                keyboard.add(
                    KeyboardButton(text="⬅️ Назад", callback_data="back"),
                    KeyboardButton(text="🍃 Уволиться", callback_data="admin_retire")
                )

                await message.answer(
                    f"👋 Привет, [{nickname}](https://t.me/{username}), ты являешься лимитированный администратором.\n \n"
                    f"✅ Тебе доступны следующие функции:\n \n"
                    f"🔹 `Выдать крутки`\n"
                    f"🔹 `Выдать пасс`\n\n"
                    f"❌ Тебе не доступны следующие функции:\n \n"
                    f"🔹 `Выдать себе крутки`\n"
                    f"🔹 `Выдать себе пасс`\n"
                    f"🔹 `Промокоды`\n"
                    f"🔹 `Пользователи`\n\n"
                    f"🗒 Ты можешь уволиться в любое время нажав на кнопку, или написав в чат: \"`Уволиться`\"\n\n"
                    f"🐣 Пропиши в чат комманду /admin чтобы ознакомиться с функциями администратора.\n",
                    parse_mode="Markdown", 
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
            
            elif admin_role == "advanced":

                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки"),
                    KeyboardButton(text="🔑 Выдать пасс"),
                    KeyboardButton(text="✍️ Написать сообщение владельцу")
                )

                keyboard.add(
                    KeyboardButton(text="👮 Администраторы"),
                )

                keyboard.add(
                    KeyboardButton(text="💬 Промокоды"),
                    KeyboardButton(text="🌀 Выдать себе крутки"),
                    KeyboardButton(text="🔑 Выдать себе пасс")
                )

                keyboard.add(
                    KeyboardButton(text="😐 Пользователи"),
                )

                keyboard.add(
                    KeyboardButton(text="⬅️ Назад"),
                    KeyboardButton(text="🍃 Уволиться")
                )

                await message.answer(
                    f"👋 Привет, [{nickname}](https://t.me/{username}), ты являешься продвинутым администратором.\n \n"
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
                    f"🗒 Ты можешь уволиться в любое время нажав на кнопку, или написав в чат: \"`Уволиться`\"\n\n"
                    f"🐣 Пропиши в чат комманду /admin чтобы ознакомиться с функциями администратора.\n",
                    parse_mode="Markdown", 
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )

            elif admin_role == "owner":

                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки"),
                    KeyboardButton(text="🔑 Выдать пасс"),
                )

                keyboard.add(
                    KeyboardButton(text="👮 Администраторы"),
                )

                keyboard.add(
                    KeyboardButton(text="💬 Промокоды"),
                    KeyboardButton(text="🌀 Выдать себе крутки"),
                    KeyboardButton(text="🔑 Выдать себе пасс")
                )

                keyboard.add(
                    KeyboardButton(text="😐 Пользователи"),
                )

                keyboard.add(
                    KeyboardButton(text="🔄 Обновиться"),
                    KeyboardButton(text="🔴 Выключить бота"),
                    KeyboardButton(text="🎆 Ивенты")
                )

                keyboard.add(
                    KeyboardButton(text="⬅️ Назад"),
                    KeyboardButton(text="💹 Статистика")
                )


                await message.answer(
                    f"👋 Привет, [{nickname}](https://t.me/{username}), ты являешься владельцем бота.\n \n"
                    f"✅ Тебе доступны все функции:\n \n"
                    f"🔹 `Выдать себе крутки`\n"
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
                    f"🔹 `Выключить бота`\n\n"
                    f"🐣 Пропиши в чат комманду /admin чтобы ознакомиться с функциями администратора.\n",
                    parse_mode="Markdown", 
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )

    else:
        await admin_message_handler(message)
