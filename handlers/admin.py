from config import BOT_TOKEN
from rate_limit import rate_limit
from db import db
from dp import dp, bot
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import subprocess
import os
import sys
from keyboards.main_keyboard import get_main_keyboard

# commands=["admin","add_admin", "remove_admin", "ban", "unban",  "promote", "admins", 
# "users", "stats", "promo", "add_promo", "stop", "update", "events", "add_event",
# "give_spin", "give_pass", "self_spin", "self_pass"]


@rate_limit(0.5)
async def admin_commands(message: types.Message):

    user_id = message.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    admin_data = db.admins.find_one({"user_id": user_id})

    if not admin_data:
        await message.answer(
            f"🚫 [{nickname}](https://t.me/{username}), вы не являетесь администратором бота.",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    
    if not user_data:
        await message.answer("❌ Пользователь не найден, пожалуйста, сначала введите команду /start.")
        return
    
    admin_data = db.admins.find_one({"user_id": user_id})
    admin_role = admin_data.get("role", "limited")
    parts = message.text.strip().lower().split(" ")
    nickname = user_data.get("nickname", "Гость")
    username = user_data.get("username")

    if message.text.startswith("/admin"):
        admin_data = db.admins.find_one({"user_id": user_id})  # Fetch admin data
        admins = db.admins.find()  # Fetch list of admins

        if not admin_data:
            await message.answer(
                f"🚫 [{nickname}](https://t.me/{username}), вы не являетесь администратором бота.",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

        else:
            admin_role = admin_data.get("role")  # Get role after confirming admin_data exists
            keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)

            # Limited admin functionality
            if admin_role == "limited":
                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки"),
                    KeyboardButton(text="🔑 Выдать пасс"),
                    KeyboardButton(text="✍️ Написать сообщение владельцу")
                )
                keyboard.add(
                    KeyboardButton(text="⬅️ Назад"),
                    KeyboardButton(text="🍃 Уволиться")
                )

                await message.answer(
                    f"👋 Привет, [{nickname}](https://t.me/{username}), ты являешься лимитированный администратором.\n\n"
                    f"✅ Тебе доступны следующие функции:\n\n"
                    f"🔹 Выдать крутки - /give_spin <user_id> <количество>\n"
                    f"🔹 Выдать пасс - /give_pass <user_id> <количество дней>\n\n"
                    f"❌ Тебе не доступны следующие функции:\n\n"
                    f"🔹 Выдать себе крутки\n"
                    f"🔹 Выдать себе пасс\n"
                    f"🔹 Промокоды\n"
                    f"🔹 Пользователи\n"
                    f"🔹 Администраторы - /admins\n"
                    f"🔹 Ивенты (мифический день, босс, новый сезон, летние и зимние ивенты)\n\n"
                    f"🗒 Ты можешь уволиться в любое время нажав на кнопку, или написав в чат: \"`Уволиться`\"",
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )

            # Advanced admin functionality
            elif admin_role == "advanced":
                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки"),
                    KeyboardButton(text="🔑 Выдать пасс"),
                    KeyboardButton(text="✍️ Написать сообщение владельцу")
                )
                keyboard.add(KeyboardButton(text="👮 Администраторы"))
                keyboard.add(
                    KeyboardButton(text="💬 Промокоды"),
                    KeyboardButton(text="🌀 Выдать себе крутки"),
                    KeyboardButton(text="🔑 Выдать себе пасс")
                )
                keyboard.add(KeyboardButton(text="😐 Пользователи"))
                keyboard.add(
                    KeyboardButton(text="⬅️ Назад"),
                    KeyboardButton(text="🍃 Уволиться")
                )

                await message.answer(
                    f"👋 Привет, [{nickname}](https://t.me/{username}), ты являешься продвинутым администратором.\n\n"
                    f"✅ Тебе доступны продвинутые функции:\n\n"
                    f"🔹 Выдать себе крутки - /self_spin <количество>\n"
                    f"🔹 Выдать себе пасс - /self_pass <количество дней>\n"
                    f"🔹 Выдать крутки - /give_spin <user_id> <количество>\n"
                    f"🔹 Выдать пасс - /give_pass <user_id> <количество дней>\n"
                    f"🔹 Промокоды - /promo\n"
                    f"🔹 Пользователи - /users\n"
                    f"🔹 Администраторы - /admins\n\n"
                    f"❌ Тебе не доступны следующие функции:\n\n"
                    f"🔹 Ивенты (мифический день, босс, новый сезон, летние и зимние ивенты)\n\n"
                    f"🗒 Ты можешь уволиться в любое время нажав на кнопку, или написав в чат: \"`Уволиться`\"",
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )


            # Owner admin functionality
            elif admin_role == "owner":
                keyboard.add(
                    KeyboardButton(text="🌀 Выдать крутки"),
                    KeyboardButton(text="🔑 Выдать пасс")
                )
                keyboard.add(KeyboardButton(text="👮 Администраторы"))
                keyboard.add(
                    KeyboardButton(text="💬 Промокоды"),
                    KeyboardButton(text="🌀 Выдать себе крутки"),
                    KeyboardButton(text="🔑 Выдать себе пасс")
                )
                keyboard.add(KeyboardButton(text="😐 Пользователи"))
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
                    f"👋 Привет, [{nickname}](https://t.me/{username}), ты являешься владельцем бота.\n\n"
                    f"✅ Тебе доступны все функции:\n\n"
                    f"🔹 Выдать себе крутки - /self_spin <количество>\n"
                    f"🔹 Выдать себе пасс - /self_pass <количество дней>\n"
                    f"🔹 Выдать крутки - /give_spin <user_id> <количество>\n"
                    f"🔹 Выдать пасс - /give_pass <user_id> <количество дней>\n"
                    f"🔹 Промокоды - /promo\n"
                    f"🔹 Пользователи - /users\n"
                    f"🔹 Администраторы - /admins\n"
                    f"🔹 Ивенты - /events\n"
                    f"🔹 Статистика - /stats\n"
                    f"🔹 Обновить бота - /update\n"
                    f"🔹 Выключить бота - /stop",
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )

    elif message.text.startswith("/add_admin"):

        if len(parts) < 3:
            await message.answer("❌ Укажите команду в формате: /add_admin <user_id> <role>")
            return

        target_user_id = int(parts[1])
        target_user = db.users.find_one({"user_id":target_user_id})
        target_role = parts[2]
        target_nickname = target_user.get("nickname","Гость")
        target_username = target_user.get("username")
        if target_role not in ["limited", "advanced"]:
            await message.answer("❌ Роль должна быть `limited` или `advanced`.")
            return

        if admin_role in ["owner", "advanced"]:
            target_user = db.users.find_one({"user_id": target_user_id})
            target_nickname = target_user.get("nickname","Гость")
            target_username = target_user.get("username")
            if not target_user:
                await message.answer("❌ Пользователь не найден.")
                return
            
            limit = "no_limit" if target_role != "limited" else 10000
            
            if target_role == "advanced":
                self_spins = 1000

            elif target_role == "limited":
                self_spins = 0

            db.admins.insert_one({"user_id": target_user_id, "role": target_role, "self_spins":self_spins, "spins":limit})
            await message.answer(f"✅ Пользователь [{target_nickname}](https://t.me/{target_username}) добавлен как администратор \"{target_role}\".", parse_mode="Markdown",disable_web_page_preview=True)
            await bot.send_message(chat_id=target_user_id, text=f"✅ [{target_nickname}](https://t.me/{target_username}), ты теперь администратор этого бота. (Твой уровень: {target_role})", parse_mode="Markdown",disable_web_page_preview=True)
        else:
            await message.answer("🚫 Недостаточно прав для выполнения этой команды.")

    elif message.text.startswith("/remove_admin"):
        
        if len(parts) < 2:
            await message.answer("❌ Укажите команду в формате: /remove_admin <user_id>")
            return

        target_user_id = int(parts[1])
        target_user = db.users.find_one({"user_id": target_user_id})
        target_role = db.admins.find_one({"user_id":target_user_id})
        target_nickname = target_user.get("nickname","Гость")
        target_username = target_user.get("username")

        if admin_role == "owner":

            target_user = db.users.find_one({"user_id": target_user_id})
            target_nickname = target_user.get("nickname","Гость")
            target_username = target_user.get("username")
            if not target_user:
                await message.answer("❌ Пользователь не найден.")
                return
            
            db.admins.find_one_and_delete({"user_id": target_user_id})
            await message.answer(f"✅ Пользователь [{target_nickname}](https://t.me/{target_username}) больше не является администратором.", parse_mode="Markdown",disable_web_page_preview=True)
        
        elif admin_role == "advanced" and target_role not in ["owner", "limited"]:

            target_user = db.users.find_one({"user_id": target_user_id})
            target_nickname = target_user.get("nickname","Гость")
            target_username = target_user.get("username")

            if not target_user:
                await message.answer("❌ Пользователь не найден.")
                return
            
            db.admins.find_one_and_delete({"user_id": target_user_id})
            await message.answer(f"✅ Пользователь [{target_nickname}](https://t.me/{target_username}) больше не является администратором.", parse_mode="Markdown",disable_web_page_preview=True)
            await bot.send_message(chat_id=target_user_id, text=f"[{target_nickname}](https://t.me/{target_username}), ты больше не являешься администратором бота. 😔", parse_mode="Markdown",disable_web_page_preview=True)
        
        elif admin_role == "advanced" and target_role in ["owner", "advanced"]:

            await message.answer("❌ Нельзя удалить администратора с ролью \"owner\" или \"advanced\".")

        else:

            await message.answer("🚫 Недостаточно прав для выполнения этой команды.")

    elif message.text.startswith("/ban"):

        if len(parts) < 3:
            await message.answer("❌ Укажите команду в формате: /ban <user_id> <причина блокировки>")
            return
        
        message.text.strip().lower().split(" ", maxsplit=3)
        target_user_id = int(parts[1])
        target_role = db.admins.find_one({"user_id":target_user_id})
        reason = parts[2]
        banned_user = db.banned.find_one({"user_id":target_user_id})

        if admin_role in ["advanced", "owner"]:

            target_user = db.users.find_one({"user_id": target_user_id})

            if not target_user:
                await message.answer(
                    f"🚫 Не удалось найти пользователя с ID: {target_user_id}",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

            if banned_user:
                await message.answer(
                    f"🚫 Пользователь с ID: {target_user_id}, уже находится в списке заблокированных пользователей.",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

            else: 
                
                target_nickname = target_user.get("nickname","Гость")
                target_username = target_user.get("username")
    
                db.banned.insert_one(target_user)
                db.users.find_one_and_delete({"user_id": target_user_id})


                await message.answer("✅")
                await message.answer(
                    f"Пользователь [{target_nickname}](https://t.me/{target_username}), был успешно заблокирован."
                    f"Причина блокировки: {reason}",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

                await bot.send_message(
                    chat_id=target_user_id,
                    text=f"[{target_nickname}](https://t.me/{target_username}), вы были заброкированы администраторами бота. \nПричина блокировки: {reason}",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )


    elif message.text.startswith("/update"):
        if admin_role in ["owner", "advanced"]:
            await message.answer("🔄 Обновление бота... Пожалуйста, подождите.")
            try:
                result = subprocess.run(["git", "pull"], capture_output=True, text=True, check=True)
                git_output = result.stdout.strip() or "No output from Git."
                await message.answer(f"✅ Обновления синхронизированы:\n`\n{git_output}\n`", parse_mode="Markdown")

                if git_output != "Already up to date.":
                    await message.answer("♻️ Перезапускаю бота...")
                    os.execl(sys.executable, sys.executable, *sys.argv)
            except Exception as e:
                await message.answer(f"❌ Не удалось обновить бота:\n{e}")
        else:
            await message.answer("🚫 Недостаточно прав для выполнения этой команды.")

    elif message.text.startswith("/promote"):
        
        if len(parts) < 3:
            await message.answer("❌ Укажите команду в формате: /promote <user_id> <role>")
            return
        
        target_user_id = int(parts[1])
        target_user = db.users.find_one({"user_id":target_user_id})
        target_nickname = target_user.get("nickname","Гость")
        target_username = target_user.get("username")
        new_role = parts[2]
        target_role = new_role

        if new_role not in ["limited", "advanced"]:
            await message.answer("❌ Роль должна быть `limited` или `advanced`.")
            return

        if admin_role in ["owner", "advanced"]:

            target_user = db.users.find_one({"user_id": target_user_id})

            if not target_user:
                await message.answer("❌ Пользователь не найден.")
                return
            
            limit = "no_limit" if new_role != "limited" else "10000"

            if new_role == "advanced":
                self_spins = 1000

            elif new_role == "limited":
                self_spins = 500

            db.admins.update_one({"user_id": target_user_id}, {"$set": {"role": new_role, "spins": limit, "self_spins":self_spins}})
            
            await message.answer(f"✅ Роль пользователя [{target_nickname}](https://t.me/{target_username}) изменена на \"{new_role}\".", parse_mode="Markdown",disable_web_page_preview=True)
            
            await bot.send_message(
                chat_id=target_user_id, 
                text=f"✅ [{target_nickname}](https://t.me/{target_username}), тебя повысили до {target_role}. (Твой уровень: {target_role})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        
        else:
            await message.answer("🚫 Недостаточно прав для выполнения этой команды.")
    
    elif message.text.startswith("/give_spin"):

        if len(parts) < 3:
            await message.answer("❌ Укажите команду в формате: /give_spin <user_id> <количество>")
            return

        target_user_id = int(parts[1])
        target_user = db.users.find_one({"user_id":target_user_id})

        users_spin_chances = target_user.get("spin_chances", 0)
        target_nickname = target_user.get("nickname","Гость")
        target_username = target_user.get("username")

        spin_chances = int(parts[2])
        limit = admin_data.get("spins")

        if admin_role == "owner":
            db.users.update_one({"user_id":target_user_id},{"$set":{"spin_chances":users_spin_chances+spin_chances}})


            await message.answer("✅")
            await message.answer(
                f"Пользователю [{target_nickname}](https://t.me/{target_username}) успешно выдали {spin_chances} круток.\n",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

            await bot.send_message(chat_id=target_user_id, text=f"🃏 [{target_nickname}](https://t.me/{target_username}), администраторы бота выдали тебе {spin_chances} круток.", parse_mode="Markdown", disable_web_page_preview = True)



        elif admin_role == "advanced":

            if target_user_id == user_id:
                await message.answer("❌")
                await message.answer(
                    f"❌ [{nickname}](https://t.me/{username}), нельзя выдавать крутки себе, используя эту команду.\n\n"
                    f"🃏 Используйте команду `/self_spin <количество> чтобы получить крутки для себя.\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

            else:

                db.users.update_one({"user_id":target_user_id},{"$set":{"spin_chances":users_spin_chances+spin_chances}})

                await message.answer("✅")
                await message.answer(
                    f"Пользователю [{target_nickname}](https://t.me/{target_username}) успешно выдали {spin_chances} круток.\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                
                await bot.send_message(chat_id=target_user_id, text=f"🃏 [{target_nickname}](https://t.me/{target_username}), администраторы бота выдали тебе {spin_chances} круток.", parse_mode="Markdown", disable_web_page_preview = True)


        elif admin_role == "limited":

            if target_user_id == user_id:
                await message.answer("❌")
                await message.answer(
                    f"❌ [{nickname}](https://t.me/{username}), нельзя выдавать крутки себе, используя эту команду.\n\n"
                    f"🃏 Используйте команду `/self_spin <количество> чтобы получить крутки для себя.\n",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            
            else: 

                if limit - spin_chances >= 0:

                    db.admins.update_one({"user_id":user_id}, {"$set":{"spin":(limit-spin_chances)}})
                    db.users.update_one({"user_id":target_user_id},{"$set":{"spin_chances":users_spin_chances+spin_chances}})

                    await message.answer("✅")
                    await message.answer(
                        f"Пользователю [{target_nickname}](https://t.me/{target_username}) успешно выдали {spin_chances} круток.\n"
                        f"😉 Ваш оставшийся лимит: {limit-spin_chances}.",
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
    
                    await bot.send_message(chat_id=target_user_id, text=f"🃏 [{target_nickname}](https://t.me/{target_username}), администраторы бота выдали тебе {spin_chances} круток.", parse_mode="Markdown", disable_web_page_preview = True)

                else:
                    await message.answer("❌")
                    await message.answer(
                        f"Пользователю [{target_nickname}](https://t.me/{target_username}) не удалось выдать {spin_chances} круток.\n"
                        f"😉 Ваш оставшийся лимит: {limit}.",
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
        
        else: 
            await message.answer("❌")
            await message.answer(
                f"[{user_id}](https://t.me/{username}), введите команду в формате: `/give_spin <user_id> <количество>.\n",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

    elif message.text.startswith("/self_spin"):
        
        if len(parts) < 2:
            await message.answer("❌ Укажите команду в формате: /self_spin <количество>")
            return
        
        user_id = message.from_user.id
        user_data = db.users.find_one({"user_id":user_id})

        us_spin_chances = user_data.get("spin_chances",0)
        self_spins = admin_data.get("self_spins",0)

        spin_chances = int(parts[1])
        limit = admin_data.get("spins")

        if admin_role == "owner":
            db.users.update_one({"user_id":user_id},{"$set":{"spin_chances":us_spin_chances+spin_chances}})

            await message.answer("✅")
            await message.answer(
                f"✅ Вы выдали себе {spin_chances} круток\n",
                parse_mode="Markdown"
            )


        elif admin_role in ["advanced"]:

            if self_spins>=spin_chances:

                db.users.update_one({"user_id":user_id},{"$set":{"spin_chances":spin_chances+spin_chances}})
                db.admins.update_one({"user_id":user_id},{"$set":{"self_spins":self_spins-spin_chances}})                

                await message.answer("✅")
                await message.answer(
                    f"✅ Вы выдали себе {spin_chances} круток.\n\n"
                    f"😉 Ваш оставшийся лимит: {self_spins-spin_chances}.",
                    parse_mode="Markdown"
                )

            else:

                await message.answer("❌")
                await message.answer(
                    f"❌ Не удалось выдать вам {spin_chances} круток, у вас не хватает лимита.\n\n"
                    f"😉 Ваш оставшийся лимит: {self_spins}.",
                    parse_mode="Markdown"
                )

        else: 
            await message.answer("❌")
            await message.answer(
                f"❌ Не удалось выдать вам {spin_chances} круток, у вас не хватает лимита.\n\n"
                f"😉 Ваш оставшийся лимит: {self_spins}.",
                parse_mode="Markdown"
            )
   
@rate_limit(0.5)
async def admin_message_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    admin_data = db.admins.find_one({"user_id": user_id})

    user_input = message.text.strip().lower()

    if not admin_data:
        await message.answer("🚫 Вы не авторизованы или не являетесь администратором.")
        return  # Stop further execution

    elif "обновиться" in user_input:
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
                await message.answer("♻️ Перезапускаю бота...", reply_markup=get_main_keyboard(user_id))
                os.execl(sys.executable, sys.executable, *sys.argv)
            except Exception as e:
                await message.answer(f"❌ Не удалось перезапустить бота:\n{e}", reply_markup=get_main_keyboard(user_id))

    elif "назад" in user_input:
        await message.answer("👋", reply_markup=get_main_keyboard(user_id))

    elif "написать сообщение владельцу" in user_input:
        await message.answer("Вы выбрали: написать сообщение владельцу.")
    
    else:
        # Unknown command, ignore or send a generic response
        await message.answer("❓ Неизвестная команда. Пожалуйста, выберите доступный вариант из меню.")
