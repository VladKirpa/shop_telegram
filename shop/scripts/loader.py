from shop.scripts.config import BOT_TOKEN, ADMIN, CRYPTOBOT_API_TOKEN
import telebot

admin = ADMIN
bot = telebot.TeleBot(BOT_TOKEN)
cb_token = CRYPTOBOT_API_TOKEN