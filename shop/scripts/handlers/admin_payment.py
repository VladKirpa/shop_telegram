from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from shop.scripts.loader import bot
from shop.scripts.utils.payment_config import (
    load_config, save_config,
    get_card_details, update_card_details
)


def build_payment_admin_keyboard():
    config = load_config()
    enabled = config.get("enabled_methods", [])
    kb = InlineKeyboardMarkup()

    for method in ["crypto", "card"]:
        status = "✅ Включено" if method in enabled else "❌ Выключено"
        kb.add(InlineKeyboardButton(f"{method.upper()} — {status}", callback_data=f"toggle_{method}"))

    kb.add(InlineKeyboardButton("✏️ Редактировать карту", callback_data="edit_card"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_back"))
    return kb


@bot.message_handler(commands=["payment_settings"])
def handle_payment_settings(message: Message):
    kb = build_payment_admin_keyboard()
    bot.send_message(message.chat.id, "🏦 Настройки оплаты:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("toggle_"))
def handle_toggle_payment_method(call):
    method = call.data.replace("toggle_", "")
    config = load_config()
    enabled = config.get("enabled_methods", [])

    if method in enabled:
        enabled.remove(method)
    else:
        enabled.append(method)

    config["enabled_methods"] = enabled
    save_config(config)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=build_payment_admin_keyboard())


@bot.callback_query_handler(func=lambda c: c.data == "edit_card")
def handle_edit_card_request(call):
    bot.send_message(call.message.chat.id, "✏️ Отправь данные карты в формате:\n<Номер>\n<Банк>\n<Получатель>")
    bot.register_next_step_handler(call.message, handle_card_details_update)


def handle_card_details_update(message: Message):
    lines = message.text.strip().split("\n")
    if len(lines) < 3:
        bot.send_message(message.chat.id, "❌ Неверный формат. Попробуй ещё раз.")
        return

    number, bank, receiver = lines[0], lines[1], lines[2]
    update_card_details(number, bank, receiver)
    bot.send_message(message.chat.id, "✅ Реквизиты карты обновлены!")