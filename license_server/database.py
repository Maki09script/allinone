import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'licenses.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            hwid TEXT,
            type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_banned BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def create_license(key, license_type, duration_days=None):
    conn = get_db_connection()
    expires_at = None
    if duration_days:
        # Don't set expiry yet for timed keys. Wait for activation.
        expires_at = None
    
    try:
        conn.execute('INSERT INTO licenses (key, type, expires_at) VALUES (?, ?, ?)',
                     (key, license_type, expires_at))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_license(key):
    conn = get_db_connection()
    license_data = conn.execute('SELECT * FROM licenses WHERE key = ?', (key,)).fetchone()
    conn.close()
    return license_data

def activate_license(key, duration_days):
    """Sets the expiration date starting from NOW."""
    conn = get_db_connection()
    expires_at = datetime.datetime.now() + datetime.timedelta(days=duration_days)
    conn.execute('UPDATE licenses SET expires_at = ? WHERE key = ?', (expires_at, key))
    conn.commit()
    conn.close()


def update_license_hwid(key, hwid):
    conn = get_db_connection()
    conn.execute('UPDATE licenses SET hwid = ? WHERE key = ?', (hwid, key))
    conn.commit()
    conn.close()

def reset_hwid(key):
    conn = get_db_connection()
    conn.execute('UPDATE licenses SET hwid = NULL WHERE key = ?', (key,))
    conn.commit()
    conn.close()

def delete_license(key):
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM licenses WHERE key = ?', (key,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted > 0
