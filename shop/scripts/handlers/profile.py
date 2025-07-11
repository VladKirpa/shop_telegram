import telebot
import sqlite3
from shop.scripts.loader import bot
from shop.scripts.database import user_base
from telebot import types
from shop.scripts.utils import get_or_upload_photo_id

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

    