import sqlite3


def connect_db():
    return sqlite3.connect('shop.db') 


def create_categories_table():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )
    """)
    conn.commit()
    conn.close()


def add_category_column_to_products():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже колонка category_id в таблице products
    cursor.execute("PRAGMA table_info(products);")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Если колонка не существует, добавляем её
    if 'category_id' not in columns:
        cursor.execute("""ALTER TABLE products ADD COLUMN category_id INTEGER""")
        conn.commit()
    
    conn.close()


def database_init():
    conn = connect_db()
    cursor = conn.cursor()

    #users table
    cursor.execute("""CREATE TABLE IF NOT EXISTS  users (
                   id INTEGER PRIMARY KEY,
                   username TEXT,
                   balance REAL DEFAULT 0.0,
                   register_date INTEGER)""")
    
    #products table
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
                   id INTEGER PRIMARY KEY,
                   name TEXT,
                   price REAL,
                   description TEXT,
                   category TEXT)""")
    
    #deposits table
    cursor.execute("""CREATE TABLE IF NOT EXISTS deposits (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER,
                   amount REAL,
                   date INTEGER,
                   FOREIGN KEY(user_id) REFERENCES users(id))""")
    
    #orders table
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
                   id INTEGER PRIMARY KEY,
                   user_id INTEGER,
                   product_id INTEGER,
                   status TEXT,
                   date INTEGER,
                   FOREIGN KEY(user_id) REFERENCES users(id),
                   FOREIGN KEY(product_id) REFERENCES products(id))""")
    

    cursor.execute("""CREATE TABLE IF NOT EXISTS admins (
                   id INTEGER PRIMARY KEY,
                   username TEXT)""")
    
    create_categories_table()
    add_category_column_to_products()
    
    conn.commit()
    conn.close()

