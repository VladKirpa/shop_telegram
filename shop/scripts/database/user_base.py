import sqlite3
import time
from shop.scripts.database.db import connect_db
from shop.scripts.loader import bot


def add_user(user_id, username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (id, username, register_date) VALUES (?, ?, ?)',
                   (user_id, username, int(time.time())))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_balance(user_id, amount):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
    conn.commit()
    conn.close()

