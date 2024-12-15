from rate_limit import rate_limit
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db import db

@rate_limit(5) 
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
            InlineKeyboardButton(text="✅ Я оплатил", url="t.me/aniverseclone_don")
    )
        
    keys.add(
            InlineKeyboardButton(text="✏️ Другие Способы", callback_data="alternative_payment_aniverse_pass")  
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
async def alternative_payment(callback_query: types.CallbackQuery):

    # Acknowledge the callback
    await callback_query.answer()
    
    user_id = callback_query.from_user.id
    
    purchase_type = callback_query.data.split("_", maxsplit=2)[2] 
    
    # Create the keyboard with the payment link button
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="📥 Отправить чек", url="t.me/donshirley")
    )

    if purchase_type == "aniverse_pass":
        
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_paymentaniverse")
        )

    elif purchase_type == "разбан_пользователя": 

        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_welcome")
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
