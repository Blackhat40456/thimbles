import sqlite3
from config import OWNER_ID

def is_admin(user_id):
    return user_id == OWNER_ID

def add_user(chat_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users
