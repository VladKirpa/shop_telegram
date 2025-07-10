import telebot
from telebot import types
import sqlite3
from shop.scripts.loader import bot


@bot.message_handler(commands=['catalog'])
def show_catalog(message):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products")
    products = cursor.fetchall()
    conn.close()

    if not products:
        bot.send_message(message.chat.id, "No products available.")
        return

    markup = types.InlineKeyboardMarkup()
    for product in products:
        button = types.InlineKeyboardButton(product[0], callback_data=f'view_product_{product[0]}')
        markup.add(button)

    bot.send_message(message.chat.id, "Here are the products:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_product_'))
def view_product(call):
    product_name = call.data.split('_')[2]  # Извлекаем имя продукта из callback_data

    # Получаем информацию о выбранном продукте
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, price FROM products WHERE name=?", (product_name,))
    product = cursor.fetchone()
    conn.close()

    if product:
        bot.send_message(call.message.chat.id, 
                         f"Product name: {product[0]}\n"
                         f"Description: {product[1]}\n"
                         f"Price: {product[2]} USD")
    else:
        bot.send_message(call.message.chat.id, "Product not found.")