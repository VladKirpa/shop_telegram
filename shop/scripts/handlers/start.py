import telebot 
from shop.scripts.loader import bot, admin
from telebot import types
from shop.scripts.handlers import profile, catalog
from shop.scripts.handlers.addadmin import add_admin, is_admin
from shop.scripts.database import db
from shop.scripts.database import user_base

admin_id = 6659521053

# чтобы добавить в дальнейшем фото использовать это \ добавить фото в проект \ в отдельную дерикт \ открыть выбранное фото\ вывести в начале или с текстом
    # file = open("./путь к файлу.jpeg", 'rb - на чтение')
    # bot.send_photo(message.chat.id, file)
    # это добавить в вывод сенд месаджа

@bot.message_handler(commands=['start'])
def start(message):
    
    user_id = message.from_user.id
    username = message.from_user.username
    mcid = message.chat.id

    db.database_init()

    if user_id == admin_id:
        if not is_admin(user_id):
            add_admin(user_id, username)
            bot.send_message(message.chat.id, "You are now an admin.")
        

    user_info = user_base.get_user(user_id)
    if user_info:
        first_name = user_info[1]
        username = user_info[2]
    else:
        user_base.add_user(user_id, username)
    

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Profile 👤')
    button2 = types.KeyboardButton('Catalog 🛍')
    button3 = types.KeyboardButton('Support 🆘')
    markup.row(button1)
    markup.row(button2, button3)
    bot.send_message(mcid, 'start description here "For example best shop choose catalog to buy item"', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

def on_click(message):
    if message.text == 'Profile 👤':
        profile.show_profile(message)
    elif message.text == 'Catalog 🛍':
        catalog.show_catalog(message)

