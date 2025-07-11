import telebot
from telebot import types
import sqlite3
from shop.scripts.loader import bot
import json
from shop.scripts.utils import get_or_upload_photo_id


@bot.message_handler(commands=['catalog'])
def show_catalog(message):


    catalog_photo = get_or_upload_photo_id('shop/media/catalog.png')
    markup = types.InlineKeyboardMarkup()

    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()

    for category in categories:
        button = types.InlineKeyboardButton(category[1], callback_data=f'category_{category[0]}')
        markup.add(button)

    bot.send_photo(message.chat.id, catalog_photo, "Select a category:", reply_markup=markup)

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
    import json
    product_id = call.data.split('_')[1]

    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, price, image_url FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        name, description, price, image_url = product
        
        try:
            photo_ids = json.loads(image_url) if image_url else []
        except Exception:
            photo_ids = [image_url] if image_url else []

        caption = (
            f"⭐️*{name}*⭐️\n\n"
            f"💵 Price: *{price}$*\n\n"
            f"ℹ️ {description}"
        )

        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("🛒 Buy", callback_data=f'buy_{product_id}')
        button2 = types.InlineKeyboardButton("⬅️ Back to Category", callback_data='back_to_category')
        markup.add(button1, button2)

        if isinstance(photo_ids, str):
            try:
                photo_ids = json.loads(photo_ids)
            except:
                photo_ids = [photo_ids]

        if len(photo_ids) == 1:
            bot.send_photo(call.message.chat.id, photo_ids[0], caption=caption, parse_mode='Markdown', reply_markup=markup)

        elif len(photo_ids) > 1:
            media = [types.InputMediaPhoto(media=photo_id) for photo_id in photo_ids]
            bot.send_media_group(call.message.chat.id, media)

            bot.send_message(call.message.chat.id, caption, parse_mode='Markdown', reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, caption, parse_mode='Markdown', reply_markup=markup)