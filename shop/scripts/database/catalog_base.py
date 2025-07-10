import sqlite3
from shop.scripts.database.db import connect_db
from shop.scripts.loader import bot

def add_product(name, description, price, category):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name=?", (category,))
    category_id = cursor.fetchone()

    if category_id:
        category_id = category_id[0]
    else:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
        category_id = cursor.lastrowid
        conn.commit()

    cursor.execute("INSERT INTO products (name, description, price, category_id) VALUES (?, ?, ?, ?)",
                   (name, description, price, category_id))
    conn.commit()
    conn.close()


def get_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    
    return products

def update_products(id, name, description, price, category):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=?, description=?, price=?, category=? WHERE id=?",
                   (name, description, price, category, id))
    
    conn.commit()
    conn.close()


def delete_product(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id))

    conn.commit()
    conn.close()

    