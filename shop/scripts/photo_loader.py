import os
import json
from telebot import types
from shop.scripts.loader import bot, admin

PHOTO_ID_DB = 'photo_ids.json'
ADMIN_ID = admin

def get_or_upload_photo_id(photo_path: str) -> str:
    filename = os.path.basename(photo_path)

    if not os.path.exists(PHOTO_ID_DB):
        with open(PHOTO_ID_DB, 'w') as f:
            json.dump({}, f)

    with open(PHOTO_ID_DB, 'r') as f:
        photo_ids = json.load(f)

    if filename in photo_ids:
        return photo_ids[filename]

    with open(photo_path, 'rb') as photo:
        msg = bot.send_photo(ADMIN_ID, photo, caption=f"📸 Saved: {filename}")
        file_id = msg.photo[-1].file_id

    photo_ids[filename] = file_id
    with open(PHOTO_ID_DB, 'w') as f:
        json.dump(photo_ids, f, indent=4)

    return file_id