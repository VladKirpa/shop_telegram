import sqlite3
from shop.scripts.database.db import connect_db
from shop.scripts.loader import bot

def add_product(name, description, price, category, image_url=None):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name=?", (category,))
    category_id = cursor.fetchone()
    if not category_id:
        cursor.execute("INSERT INTO TABLE categories (name) VALUES (?)", (category,))
        category_id = cursor.lastrowid
        conn.commit()

    cursor.execute("""
        INSERT INTO products (name, description, price, category, image_url)
        VALUES (?, ?, ?, ?, ?)
        """, (name, description, price, category, image_url))
    
    conn.commit()
    conn.close()
    return f"Product '{name}' has been added successfully!"
    

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

    