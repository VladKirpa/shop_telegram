import sqlite3


def add_image_url_column():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(products);")
    columns = [column[1] for column in cursor.fetchall()]  
    
    if 'image_url' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT;")
        conn.commit()
    
    conn.close()

def connect_db():
    return sqlite3.connect('shop.db') 


def database_init():
    conn = connect_db()
    cursor = conn.cursor()


    #users table
    cursor.execute("""CREATE TABLE IF NOT EXISTS  users (
                   id INTEGER PRIMARY KEY,
                   username TEXT,
                   balance REAL DEFAULT 0.0,
                   register_date INTEGER)""")
    
    #categories table for catalog
    cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE)""")

    #products table
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                price REAL,
                category_id INTEGER,
                image_url TEXT,
                FOREIGN KEY (category_id) REFERENCES categories(id))""") # image_url take link to your photo
    
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
    
    #admin table
    cursor.execute("""CREATE TABLE IF NOT EXISTS admins (
                   id INTEGER PRIMARY KEY,
                   username TEXT)""")
    
    #payments table
    cursor.execute("""CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    method TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    
    add_image_url_column()
    
    conn.commit()
    conn.close()

