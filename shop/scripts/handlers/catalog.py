import telebot
from telebot import types
import sqlite3
from shop.scripts.loader import bot


@bot.message_handler(commands=['catalog'])
def show_catalog(message):
    markup = types.InlineKeyboardMarkup()

    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()

    for category in categories:
        button = types.InlineKeyboardButton(category[1], callback_data=f'category_{category[0]}')
        markup.add(button)

    bot.send_message(message.chat.id, "Select a category:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
def show_products_by_category(call):
    category_id = call.data.split('_')[1]

    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category_id=?", (category_id,))
    products = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup()

    for product in products:
        button = types.InlineKeyboardButton(product[1], callback_data=f'product_{product[0]}')
        markup.add(button)

    bot.send_message(call.message.chat.id, "Select a product:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
def show_product_details(call):
    product_id = call.data.split('_')[1]

    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, price, image_url FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        name, description, price, image_url = product
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Buy", callback_data=f'buy_{product_id}')
        button2 = types.InlineKeyboardButton("Back to Category", callback_data='back_to_category')

        markup.add(button1, button2)

        bot.send_message(call.message.chat.id, 
                        f"*{name}*\n"
                        f"Price: *${price}*\n\n"
                        f"{description}\n\n"
                        f"[View Image]({image_url})", 
                        parse_mode='Markdown')