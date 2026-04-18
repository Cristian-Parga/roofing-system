# setup_demo_admin.py - Run ONCE to create presentation admin account
import sqlite3
from werkzeug.security import generate_password_hash

DB_FILE = 'roofing.db'
ADMIN_EMAIL = 'admin@test.com'
ADMIN_PASS = 'admin123'

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Check if admin already exists
cursor.execute("SELECT email FROM administrator WHERE email = ?", (ADMIN_EMAIL,))
if not cursor.fetchone():
    hashed = generate_password_hash(ADMIN_PASS)
    cursor.execute('''
        INSERT INTO administrator (name, email, password, role)
        VALUES (?, ?, ?, ?)
    ''', ('Demo Admin', ADMIN_EMAIL, hashed, 'Admin'))
    conn.commit()
    print(f"✅ Admin created: {ADMIN_EMAIL} / {ADMIN_PASS}")
else:
    print(f"ℹ️ Admin already exists. Use: {ADMIN_EMAIL} / {ADMIN_PASS}")

conn.close()