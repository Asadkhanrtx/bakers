import mysql.connector
import os
from passlib.context import CryptContext

# Use environment variables with fallbacks for production/local
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Asad@1234'),
    'database': os.getenv('DB_NAME', 'saista_bakers')
}

print(f"Connecting to database at {DB_CONFIG['host']}...")
conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

# 1. Create essential tables if they don't exist
print("Ensuring tables exist...")
tables = [
    """CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        role VARCHAR(20) DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        category VARCHAR(50),
        price DECIMAL(10,2) NOT NULL,
        image_url VARCHAR(255)
    )""",
    """CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        total_amount DECIMAL(10,2),
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        payment_mode VARCHAR(50),
        payment_status VARCHAR(50) DEFAULT 'unpaid',
        invoice_sent BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )"""
]

for sql in tables:
    cur.execute(sql)
    conn.commit()

# 2. Add columns if missing (Migration logic)
print("Checking for missing columns...")
alters = [
    "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'customer'",
    "ALTER TABLE orders ADD COLUMN payment_mode VARCHAR(50) DEFAULT NULL",
    "ALTER TABLE orders ADD COLUMN payment_status VARCHAR(50) DEFAULT 'unpaid'",
    "ALTER TABLE orders ADD COLUMN invoice_sent BOOLEAN DEFAULT FALSE",
]

for sql in alters:
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        if '1060' in str(e): # Column already exists
            continue
        print(f"Alter error: {e}")

# 3. Seed Admin User
print("Seeding admin user...")
pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
h = pwd_ctx.hash('Admin@1234')
try:
    cur.execute(
        "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (%s,%s,%s,%s,%s)",
        ('admin', 'admin@saistabakers.com', h, 'Admin User', 'admin')
    )
    conn.commit()
    print('Admin account created: admin / Admin@1234')
except Exception as e:
    if '1062' in str(e): # Duplicate entry
        cur.execute("UPDATE users SET role='admin' WHERE username='admin'")
        conn.commit()
        print('Admin account already exists (role updated)')
    else:
        print(f'Admin seeding error: {e}')

# 4. Seed Products
print("Seeding initial products...")
initial_products = [
    ('Signature Chocolate Cake', 'Cakes', 450.00, '/images/gallery/img1.jpeg'),
    ('Velvet Strawberry Dream', 'Cakes', 500.00, '/images/gallery/img2.jpeg'),
    ('Vanilla Buttercream Classic', 'Cakes', 400.00, '/images/gallery/img3.jpeg'),
    ('Choco-Chip Artisanal Cookies', 'Cookies', 150.00, '/images/gallery/img4.jpeg'),
    ('Oatmeal Raisin Healthy Bite', 'Cookies', 120.00, '/images/gallery/img5.jpeg')
]

try:
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO products (name, category, price, image_url) VALUES (%s, %s, %s, %s)",
            initial_products
        )
        conn.commit()
        print(f"Seeded {len(initial_products)} products.")
    else:
        print("Products table already has data, skipping seed.")
except Exception as e:
    print(f"Product seeding error: {e}")

cur.close()
conn.close()
print('Migration complete!')
