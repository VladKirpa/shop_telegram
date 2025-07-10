import telebot
import sqlite3
from shop.scripts.loader import bot, admin
from shop.scripts.database import catalog_base
from telebot import types


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



@bot.message_handler(commands=['addadmin'])
def add_admin_handler(message):
    if is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id, 
            'Enter the user\'s ID and username separated by a space.\n'
            'For example: 123456789 JohnDoe\n'
            'Where 123456789 is the user ID and JohnDoe is the username.'
        )
        bot.register_next_step_handler(message, process_add_admin)
    else:
        bot.send_message(message.chat.id, "You are not authorized to add admins.")
        
def process_add_admin(message):
    try:
        user_input = message.text.strip()
        user_id, username = user_input.split()
        
        user_id = int(user_id)
        add_admin(user_id, username)
        bot.send_message(message.chat.id, f'User {username} ({user_id}) has been added as an admin.')
    
    except ValueError:
        bot.send_message(message.chat.id, 'Incorrect format. Please enter both user ID and username in the format: "user_id username".')


@bot.message_handler(commands=['removeadmin'])
def remove_admin_handler(message):
    if is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id, 
            'Enter the user\'s ID and username separated by a space to remove the admin.\n'
            'For example: 123456789 JohnDoe\n'
            'Where 123456789 is the user ID and JohnDoe is the username.'
        )
        bot.register_next_step_handler(message, process_remove_admin)
    else:
        bot.send_message(message.chat.id, "You are not authorized to remove admins.")
        
def process_remove_admin(message):
    try:
        user_input = message.text.strip()
        user_id, username = user_input.split()
        
        user_id = int(user_id)
        remove_admin(user_id)
        bot.send_message(message.chat.id, f'User {username} ({user_id}) has been removed from admin panel.')
    
    except ValueError:
        bot.send_message(message.chat.id, 'Incorrect format. Please enter both user ID and username in the format: "user_id username".')

        

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


@bot.message_handler(commands=['totalrevenue'])
def totalrevenue(message):
    try:
        user_id = message.from_user.id
        revenue = get_total_revenue(user_id)
        bot.send_message(message.chat.id, f'Total cash: {revenue}')
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred while fetching the total revenue: {str(e)}")



@bot.message_handler(commands=['panel'])
def admin_panel(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        return
    
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('🎁Product Panel🎁', callback_data='product_panel')
    button2 = types.InlineKeyboardButton('🏵User Panel🏵', callback_data='user_panel')
    markup.add(button1, button2)
    
    bot.send_message(
        message.chat.id,
        '➖➖➖👑➖➖➖\nWelcome to admin panel.\nSelect what you want to continue working with.\n➖➖➖👑➖➖➖',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ['product_panel', 'user_panel'])
def choose_panel(call):
    user_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    
    if call.data == 'product_panel':  # Панель для работы с продуктами
        button1 = types.InlineKeyboardButton('🛒Add Product🛒', callback_data='add_product')
        button2 = types.InlineKeyboardButton('🫳Get Product🫳', callback_data='get_product')
        button3 = types.InlineKeyboardButton('♻️Update Product♻️', callback_data='update_product')
        button4 = types.InlineKeyboardButton('❌Delete Product❌', callback_data='delete_product')
        button5 = types.InlineKeyboardButton('⬅️Back⬅️', callback_data='back_to_panel')
        markup.add(button1, button2, button3, button4, button5)
        bot.send_message(call.message.chat.id, "➖➖➖👑➖➖➖\nPRODUCT PANEL\n➖➖➖👑➖➖➖", reply_markup=markup)
    
    elif call.data == 'user_panel':  # Панель для работы с пользователями
        button1 = types.InlineKeyboardButton('✅Add Admin✅', callback_data='add_admin')
        button2 = types.InlineKeyboardButton('❌Remove Admin❌', callback_data='remove_admin')
        button3 = types.InlineKeyboardButton('💰Total Revenue💰', callback_data='total_revenue')
        button4 = types.InlineKeyboardButton('⬅️Back⬅️', callback_data='back_to_panel')
        markup.add(button1, button2, button3, button4)
        bot.send_message(call.message.chat.id, "➖➖➖👑➖➖➖\nUSER PANEL\n➖➖➖👑➖➖➖", reply_markup=markup)

# user panel
@bot.callback_query_handler(func=lambda call: call.data == 'add_admin')
def add_admin_handler(call):
    if not is_admin(call.from_user.id):
        bot.send_message(call.message.chat.id, "You are not authorized to add admins.")
        return

    bot.send_message(call.message.chat.id, 'Enter the user ID and username separated by a space.')
    bot.register_next_step_handler(call.message, process_add_admin)


@bot.callback_query_handler(func=lambda call: call.data == 'remove_admin')
def remove_admin_handler(call):
    if not is_admin(call.from_user.id):
        bot.send_message(call.message.chat.id, "You are not authorized to remove admins.")
        return
    
    bot.send_message(call.message.chat.id, 'Enter the user ID and username separated by a space.')
    bot.register_next_step_handler(call.message, process_remove_admin)


@bot.callback_query_handler(func=lambda call: call.data == 'total_revenue')
def total_revenue_handler(call):
    if not is_admin(call.from_user.id):
        bot.send_message(call.message.chat.id, "You are not authorized to view total revenue.")
        return
    
    total_revenue = get_total_revenue(call.from_user.id)
    bot.send_message(call.message.chat.id, f'Total revenue: {total_revenue} USD')


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_panel')
def back_to_panel_handler(call):
    admin_panel(call.message)


# product panel
# add product
@bot.callback_query_handler(func=lambda call: call.data == 'add_product')
def add_product_handler(call):
    if not is_admin(call.from_user.id):
        bot.send_message(call.message.chat.id, "You are not authorized to add products.")
        return

    bot.send_message(call.message.chat.id, "Please enter the product details in this format:\nName, Description, Price, Category")

    bot.register_next_step_handler(call.message, process_add_product)

def process_add_product(message):
    try:
        product_data = message.text.strip().split(',')
        if len(product_data) != 4:
            bot.send_message(message.chat.id, "Incorrect format. Please provide the details in the format: Name, Description, Price, Category")
            return

        name, description, price, category = [data.strip() for data in product_data]

        try:
            price = float(price)
        except ValueError:
            bot.send_message(message.chat.id, "Invalid price. Please provide a valid number for the price.")
            return
        
        bot.send_message(message.chat.id, "Would you like to add a product photo? If yes, send the image, otherwise type 'skip'.")
        bot.register_next_step_handler(message, handle_image, name, description, price, category)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error processing the product data: {e}")

def handle_image(message, name, description, price, category):
    if message.text.lower() == 'skip':
        image_url = None
        add_product_to_db(name, description, price, category, image_url)
        bot.send_message(message.chat.id, f"Product {name} added successfully without image.")
    else:
        if message.content_type == 'photo':
            photo = message.photo[-1].file_id
            image_url = bot.get_file(photo).file_path
            add_product_to_db(name, description, price, category, image_url)
            bot.send_message(message.chat.id, f"Product {name} with image added successfully!")
        else:
            bot.send_message(message.chat.id, "Invalid input. Please send a photo or type 'skip'.")

def add_product_to_db(name, description, price, category, image_url):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM categories WHERE name=?", (category,))
        category_id = cursor.fetchone()

        if not category_id:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            category_id = cursor.lastrowid
            conn.commit()

        cursor.execute("INSERT INTO products (name, description, price, category_id, image_url) VALUES (?, ?, ?, ?, ?)",
                       (name, description, price, category_id, image_url))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error adding product to DB: {e}")



# delete product
@bot.callback_query_handler(func=lambda call: call.data == 'delete_product')
def delete_product_handler(call):
    if not is_admin(call.from_user.id):
        bot.send_message(call.message.chat.id, "You are not authorized to delete products.")
        return
    
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    conn.close()
    
    markup = types.InlineKeyboardMarkup()
    for product in products:
        button = types.InlineKeyboardButton(product[1], callback_data=f'delete_product_{product[0]}')
        markup.add(button)
    
    bot.send_message(call.message.chat.id, "Select a product to delete:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_product_'))
def confirm_delete_product(call):
    product_id = call.data.split('_')[2]
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

    bot.send_message(call.message.chat.id, f"Product with ID {product_id} has been deleted.")

# update product
@bot.callback_query_handler(func=lambda call: call.data == 'update_product')
def update_product_handler(call):
    if not is_admin(call.from_user.id):
        bot.send_message(call.message.chat.id, "You are not authorized to update products.")
        return
    

    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    conn.close()
    
    markup = types.InlineKeyboardMarkup()
    for product in products:
        button = types.InlineKeyboardButton(product[1], callback_data=f'update_product_{product[0]}')
        markup.add(button)
    
    bot.send_message(call.message.chat.id, "Select a product to update:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('update_product_'))
def process_update_product(call):
    product_id = call.data.split('_')[2]

    bot.send_message(call.message.chat.id, "Please enter the new product details (name, description, price, category), separated by commas.")
    bot.register_next_step_handler(call.message, update_product_details, product_id)

def update_product_details(message, product_id):
    try:
        
        product_data = message.text.strip().split(',')
        if len(product_data) != 4:
            bot.send_message(message.chat.id, "Incorrect format. Please provide the details in the format: Name, Description, Price, Category")
            return
        
        name, description, price, category = [data.strip() for data in product_data]
        
        
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name=?", (category,))
        category_id = cursor.fetchone()
        
        if not category_id:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            category_id = cursor.lastrowid
            conn.commit()
        

        cursor.execute("UPDATE products SET name=?, description=?, price=?, category_id=? WHERE id=?", 
                       (name, description, price, category_id, product_id))
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, f"Product with ID {product_id} has been updated.")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred while updating the product: {str(e)}")

