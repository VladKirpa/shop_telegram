import telebot
import sqlite3
from shop.scripts.loader import bot, admin
from shop.scripts.database import catalog_base
from telebot import types
import json
from shop.scripts.utils.photo_loader import get_or_upload_photo_id

def add_admin(user_id, username):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admins (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admins WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def is_admin(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM admins WHERE id=?", (user_id,))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

def get_total_revenue(user_id):
    try:
        if is_admin(user_id):
            conn = sqlite3.connect('shop.db')
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM deposits")
            total_revenue = cursor.fetchone()[0] or 0.0
        else:
            return 'You do not have permission to execute this command'
    except sqlite3.DatabaseError as e:
        total_revenue = 0.0
        print(f"Database error: {e}")
    finally:
        try:
            conn.close()
        except NameError:
            pass
    return total_revenue

admin_photo_buffer = {}

@bot.callback_query_handler(func=lambda call: True)
def unified_callback_handler(call):
    data = call.data

    if data == 'panel:product':
        if not is_admin(call.from_user.id): return
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('🛒Add Product🛒', callback_data='add_product'),
            types.InlineKeyboardButton('♻️Update Product♻️', callback_data='update_product'),
            types.InlineKeyboardButton('❌Delete Product❌', callback_data='delete_product'),
            types.InlineKeyboardButton('❌Delete Category❌', callback_data='delete_category'),
            types.InlineKeyboardButton('⬅️Back⬅️', callback_data='back_to_panel')
        )
        bot.send_message(call.message.chat.id, "➖➖➖👑➖➖➖\nPRODUCT PANEL\n➖➖➖👑➖➖➖", reply_markup=markup)

    elif data == 'panel:user':
        if not is_admin(call.from_user.id): return
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('✅Add Admin✅', callback_data='add_admin'),
            types.InlineKeyboardButton('❌Remove Admin❌', callback_data='remove_admin'),
            types.InlineKeyboardButton('💰Total Revenue💰', callback_data='total_revenue'),
            types.InlineKeyboardButton('⬅️Back⬅️', callback_data='back_to_panel')
        )
        bot.send_message(call.message.chat.id, "➖➖➖👑➖➖➖\nUSER PANEL\n➖➖➖👑➖➖➖", reply_markup=markup)

    elif data == 'panel:payment':
        if not is_admin(call.from_user.id): return
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('🪙 Toggle Payment Method', callback_data='toggle_payment_method'),
            types.InlineKeyboardButton('🏦 Edit Card Details', callback_data='edit_card_details'),
            types.InlineKeyboardButton('⬅️Back⬅️', callback_data='back_to_panel')
        )
        bot.send_message(call.message.chat.id, "🛠 Payment Settings", reply_markup=markup)


    elif data == 'toggle_payment_method':
        if not is_admin(call.from_user.id): return

        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT method FROM payment_config WHERE id=1")
        row = cursor.fetchone()
        current = row[0] if row else 'crypto'

        next_method = {
            'crypto': 'card',
            'card': 'both',
            'both': 'none',
            'none': 'crypto'
        }[current]

        cursor.execute("INSERT OR REPLACE INTO payment_config (id, method) VALUES (1, ?)", (next_method,))
        conn.commit()
        conn.close()

        bot.send_message(call.message.chat.id, f"✅ Payment method set to: {next_method.upper()}")


    elif data == 'edit_card_details':
        if not is_admin(call.from_user.id): return
        bot.send_message(call.message.chat.id, "✏️ Send new card info in format:\n\n`Card Number, Bank, Holder Name`", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, save_card_details)



    elif data == 'add_admin':
        if not is_admin(call.from_user.id): return
        bot.send_message(call.message.chat.id, 'Enter the user ID and username separated by a space.')
        bot.register_next_step_handler(call.message, process_add_admin)



    elif data == 'remove_admin':
        if not is_admin(call.from_user.id): return
        bot.send_message(call.message.chat.id, 'Enter the user ID and username separated by a space.')
        bot.register_next_step_handler(call.message, process_remove_admin)


    elif data == 'total_revenue':
        if not is_admin(call.from_user.id): return
        total = get_total_revenue(call.from_user.id)
        bot.send_message(call.message.chat.id, f'Total revenue: {total} USD')

    elif data == 'add_product':
        if not is_admin(call.from_user.id): return
        bot.send_message(call.message.chat.id, "Enter product as: Name, Description, Price, Category")
        bot.register_next_step_handler(call.message, process_add_product)

    elif data == 'delete_product':
        if not is_admin(call.from_user.id): return
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        for pid, name in products:
            markup.add(types.InlineKeyboardButton(name, callback_data=f'delete_product_{pid}'))
        bot.send_message(call.message.chat.id, "Select a product to delete:", reply_markup=markup)

    elif data.startswith('delete_product_'):
        pid = int(data.split('_')[2])
        result = catalog_base.delete_product(pid)
        bot.send_message(call.message.chat.id, result)

    elif data == 'delete_category':
        if not is_admin(call.from_user.id): return
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        for cid, cname in categories:
            markup.add(types.InlineKeyboardButton(cname, callback_data=f'delete_category_{cid}'))
        bot.send_message(call.message.chat.id, 'Select category to delete', reply_markup=markup)

    elif data.startswith('delete_category_'):
        cid = int(data.split('_')[2])
        result = catalog_base.delete_category(cid)
        bot.send_message(call.message.chat.id, result)

    elif data == 'update_product':
        if not is_admin(call.from_user.id): return
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        for pid, name in products:
            markup.add(types.InlineKeyboardButton(name, callback_data=f'update_product_{pid}'))
        bot.send_message(call.message.chat.id, "Select product to update:", reply_markup=markup)

    elif data.startswith('update_product_'):
        pid = int(data.split('_')[2])
        bot.send_message(call.message.chat.id, "Enter new product details (Name, Description, Price, Category)")
        bot.register_next_step_handler(call.message, update_product_details, pid)

    elif data == 'back_to_panel':
        send_admin_panel(call.message.chat.id)


def send_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('🎁Product Panel🎁', callback_data='panel:product')
    button2 = types.InlineKeyboardButton('🏵User Panel🏵', callback_data='panel:user')
    button3 = types.InlineKeyboardButton('💳 Payment 💳 ', callback_data='panel:payment' )
    markup.add(button1, button2, button3)

    bot.send_message(
        chat_id,
        '➖➖➖👑➖➖➖\nWelcome to admin panel.\nSelect what you want to continue working with.\n➖➖➖👑➖➖➖',
        reply_markup=markup
    )

@bot.message_handler(commands=['panel'])
def handle_panel_command(message):
    if is_admin(message.from_user.id):
        send_admin_panel(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_panel')
def back_to_panel_handler(call):
    if is_admin(call.from_user.id):
        send_admin_panel(call.message.chat.id)

def process_add_admin(message):
    try:
        user_id, username = message.text.strip().split()
        add_admin(int(user_id), username)
        bot.send_message(message.chat.id, f'Admin {username} ({user_id}) added.')
    except:
        bot.send_message(message.chat.id, 'Invalid format. Use: user_id username')


def process_remove_admin(message):
    try:
        user_id, username = message.text.strip().split()
        remove_admin(int(user_id))
        bot.send_message(message.chat.id, f'Admin {username} ({user_id}) removed.')
    except:
        bot.send_message(message.chat.id, 'Invalid format. Use: user_id username')


def process_add_product(message):
    try:
        name, desc, price, cat = [x.strip() for x in message.text.strip().split(',')]
        admin_photo_buffer[message.from_user.id] = {'name': name, 'description': desc, 'price': price, 'category': cat, 'photos': []}
        bot.send_message(message.chat.id, "Send photos. Type `done` when finished or `skip` to skip.", parse_mode='Markdown')
        bot.register_next_step_handler(message, handle_product_photos)
    except:
        bot.send_message(message.chat.id, "Invalid format. Use: Name, Description, Price, Category")


def handle_product_photos(message):
    uid = message.from_user.id
    if uid not in admin_photo_buffer:
        bot.send_message(message.chat.id, "Something went wrong. Start again.")
        return

    if message.content_type == 'photo':
        fid = message.photo[-1].file_id
        admin_photo_buffer[uid]['photos'].append(fid)
        bot.send_message(message.chat.id, "✅ Photo saved. More? Or type `done`.", parse_mode='Markdown')
        bot.register_next_step_handler(message, handle_product_photos)
    elif message.text.lower() == 'done':
        data = admin_photo_buffer.pop(uid)
        image_data = json.dumps(data['photos']) if len(data['photos']) > 1 else (data['photos'][0] if data['photos'] else None)
        result = catalog_base.add_product(data['name'], data['description'], data['price'], data['category'], image_data)
        bot.send_message(message.chat.id, result)
    elif message.text.lower() == 'skip':
        data = admin_photo_buffer.pop(uid)
        result = catalog_base.add_product(data['name'], data['description'], data['price'], data['category'], None)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "❌ Invalid. Send photo, or type `done` / `skip`.")
        bot.register_next_step_handler(message, handle_product_photos)


def update_product_details(message, product_id):
    try:
        name, desc, price, cat = [x.strip() for x in message.text.strip().split(',')]
        result = catalog_base.update_product(product_id, name, desc, price, cat)
        bot.send_message(message.chat.id, result)
    except:
        bot.send_message(message.chat.id, "❌ Error updating product.")


def save_card_details(message):
    try:
        number, bank, holder = [x.strip() for x in message.text.split(",")]
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid format. Please send: `Card Number, Bank, Holder`")
        return

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE payment_config SET card_number=?, card_bank=?, card_holder=? WHERE id=1", (number, bank, holder))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, f"✅ Card details updated:\n\n**{number}**\n**{bank}**\n**{holder}**", parse_mode="Markdown")
