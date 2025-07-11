import sqlite3
from shop.scripts.database.db import connect_db
from shop.scripts.loader import bot

def add_product(name, description, price, category, image_url=None):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name=?", (category,))
    category_id = cursor.fetchone()
    if not category_id:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
        category_id = cursor.lastrowid
        conn.commit()
    else:
        category_id = category_id[0]
    cursor.execute("""
        INSERT INTO products (name, description, price, category_id, image_url)
        VALUES (?, ?, ?, ?, ?)
        """, (name, description, price, category_id, image_url))
    
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

def update_product(product_id, name, description, price, category):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM categories WHERE name=?", (category,))
        category_id = cursor.fetchone()

        if not category_id:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            conn.commit()
            category_id = (cursor.lastrowid,)

        cursor.execute("""
            UPDATE products SET name=?, description=?, price=?, category=? WHERE id=?
        """, (name, description, price, category_id[0], product_id))

        conn.commit()
        return f"✅ Product ID {product_id} successfully updated."

    except Exception as e:
        return f"❌ Failed to update product: {str(e)}"

    finally:
        conn.close()



def delete_product(product_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()

        if not product:
            return f"❌ Product with ID {product_id} not found."

        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        return f"✅ Product '{product[0]}' (ID {product_id}) deleted successfully."

    except Exception as e:
        return f"❌ Failed to delete product: {str(e)}"

    finally:
        conn.close()


def delete_category(category_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE id=?", (category_id,))
        category = cursor.fetchone()

        if not category:
            return f"❌ Category with ID {category_id} not found."
        
        cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
        conn.commit()
        return f"✅ Product '{category[0]}' (ID {category_id}) deleted successfully."
    
    except Exception as e:
        return f'❌ Failed to delete product: {str(e)}'
    finally:
        conn.close()