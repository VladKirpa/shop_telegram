import telebot
import sqlite3
from shop.scripts.loader import bot
from shop.scripts.database import user_base
from telebot import types
from shop.scripts.utils.photo_loader import get_or_upload_photo_id
from shop.scripts.utils.crypto import check_crypto_payment, create_invoice
from shop.scripts.utils.payment_config import is_method_enabled, get_card_details, get_payment_config


def get_deals_info(user_id):
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id=?', (user_id,))   
    deals_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(price) FROM orders JOIN products ON orders.product_id = products.id WHERE user_id=?", (user_id,))
    deals_amount = cursor.fetchone()[0] or 0.0

    conn.close()

    return deals_amount, deals_count


@bot.message_handler(commands=['Profile 👤'])
def show_profile(message):
    profile_photo = get_or_upload_photo_id('shop/media/profile.png')

    mcid = message.chat.id
    user_id = message.from_user.id

    user_info = user_base.get_user(user_id)
    deals_amount, deals_count = get_deals_info(user_id)
    balance = user_info[2]
    

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('💸Top up Balance💸', callback_data='💸Top up Balance💸')
    button2 = types.InlineKeyboardButton('📂Purchase history📂', callback_data='📂Purchase history📂')
    button3 = types.InlineKeyboardButton('🫂Referal programm🫂', callback_data='🫂Referal programm🫂')
    button4 = types.InlineKeyboardButton('Change language', callback_data='Change language')
    markup.row(button1), markup.row(button2), markup.row(button3), markup.row(button4)
    
    bot.send_photo(
    mcid, profile_photo,
    caption=(
        f"➖➖➖ℹ️➖➖➖\n"
        f"Your ID : {user_id}\n"
        f"Your balance : {balance}$\n"
        f"Deals : {deals_count}\n"
        f"Total spent : {deals_amount}$"
    ),
    reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == '💸Top up Balance💸')
def top_up_balance(call):
    method = get_payment_config()
    
    if method == "crypto":
        msg = bot.send_message(call.message.chat.id, "💵 Enter amount in USD to top up:")
        bot.register_next_step_handler(msg, handle_amount_input)
    elif method == "card":
        card = get_card_details()
        if not card:
            bot.send_message(call.message.chat.id, "❌ Card payment temporarily unavailable.")
            return

        text = (
            f"💳 Send payment to:\n"
            f"Card: `{card['number']}`\n"
            f"Bank: `{card['bank']}`\n"
            f"Recipient: `{card['holder']}`\n\n"
            f"📸 Send screenshot as confirmation:"
        )
        msg = bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(msg, handle_card_screenshot)
    elif method == "none":
        bot.send_message(call.message.chat.id, "💬 This store doesn't support online payment.\nContact seller for instructions.")
    elif method == "both":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Crypto", callback_data='crypto_topup'),
            types.InlineKeyboardButton("Card", callback_data='card_topup')
        )
        bot.send_message(call.message.chat.id, "💵 Choose payment method:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'card_topup')
def card_topup(call):
    card = get_card_details()
    if not card:
        bot.send_message(call.message.chat.id, "❌ Card payment temporarily unavailable.")
        return

    text = (
        f"💳 Send payment to:\n"
        f"Card: `{card['number']}`\n"
        f"Bank: `{card['bank']}`\n"
        f"Recipient: `{card['holder']}`\n\n"
        f"📸 Send screenshot as confirmation:"
    )
    msg = bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(msg, handle_card_screenshot)

def handle_amount_input(message):
    try:
        amount = float(message.text)
        invoice_url = create_invoice(amount, payload=str(message.from_user.id))
        if invoice_url:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💸 Оплатить", url=invoice_url))
            markup.add(types.InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment"))
            bot.send_message(message.chat.id, f"💵 Ссылка для оплаты на сумму {amount}$", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Не удалось создать счёт. Попробуйте позже.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите корректную сумму.")


@bot.callback_query_handler(func=lambda call: call.data == "check_payment")
def handle_check_payment(call):
    user_id = call.from_user.id
    amount = check_crypto_payment(user_id)

    if amount > 0:
        current_balance = user_base.get_user(user_id)[2]
        new_balance = current_balance + amount
        user_base.update_balance(user_id, new_balance)
        bot.send_message(user_id, f"✅ Оплата подтверждена!\n💰 Ваш новый баланс: {new_balance}$")
    else:
        bot.send_message(user_id, "❌ Платёж не найден. Подождите пару минут и попробуйте снова.")


@bot.callback_query_handler(func=lambda call: call.data == 'card_topup')
def show_card_details(call):
    card = get_card_details()
    message_text = (
        f"💳 Реквизиты для перевода:\n"
        f"Номер карты: {card['number']}\n"
        f"Банк: {card['bank']}\n"
        f"Получатель: {card['receiver']}\n\n"
        "После перевода отправьте скриншот оплаты в этот чат."
    )
    bot.send_message(call.message.chat.id, message_text)

@bot.message_handler(content_types=["photo"])
def handle_card_payment_photo(message):
    if is_method_enabled("card"):
        from os import getenv
        admin_id = int(getenv("ADMIN_ID"))
        bot.forward_message(admin_id, message.chat.id, message.message_id)
        bot.reply_to(message, "📨 Скрин отправлен на проверку администратору.")

def handle_card_screenshot(message):
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Please send a valid screenshot (photo).")
        return

    photo_id = message.photo[-1].file_id

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO card_payments (user_id, file_id, status) VALUES (?, ?, ?)", (message.from_user.id, photo_id, 'pending'))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, "✅ Screenshot received. We'll verify and update your balance soon.")
