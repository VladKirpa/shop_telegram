import telebot 
from shop.scripts.loader import bot, admin
from telebot import types
from shop.scripts.handlers import profile, catalog
from shop.scripts.handlers.addadmin import add_admin, is_admin
from shop.scripts.database import db
from shop.scripts.database import user_base
from shop.scripts.utils import get_or_upload_photo_id

admin_id = 6659521053

@bot.message_handler(commands=['start'])
def start(message):
    
    start_photo = get_or_upload_photo_id('shop/media/start.png')
    
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
    start_text = "🎉 *Welcome!* Choose your option below:"
    bot.send_photo(mcid, start_photo, caption=start_text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['Profile 👤', 'Catalog 🛍', 'Support 🆘'])
def always_working_buttons(message):
    
    bot.clear_step_handler_by_chat_id(message.chat.id)

    support_photo = get_or_upload_photo_id('shop/media/support.png')

    if message.text == 'Profile 👤':
        profile.show_profile(message)
    elif message.text == 'Catalog 🛍':
        catalog.show_catalog(message)
    elif message.text == 'Support 🆘':
        bot.send_photo(
            message.chat.id, support_photo,"🆘 *Need Help from Support?*\n\n"
            "If you have any questions or issues — we’re here for you!\n"
            "📩 Contact: @Rlyvampg\n\n"
            "💼 *We also buy accounts in bulk!* If you’ve got offers for accounts or advertising — don’t hesitate to reach out.\n"
            "📬 Write directly to: @Rlyvampg",
            parse_mode='Markdown' 
        )