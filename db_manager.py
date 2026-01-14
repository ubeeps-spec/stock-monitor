import sqlite3
import hashlib
import os

DB_FILE = 'stock_app.db'

def init_db():
    """Initialize the database with users and watchlists tables."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create watchlists table
    c.execute('''
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symbols TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Register a new user. Returns True if successful, False if username exists."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        hashed_pw = hash_password(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        
        user_id = c.lastrowid
        c.execute('INSERT INTO watchlists (user_id, symbols) VALUES (?, ?)', (user_id, "TSLA, NVDA, 1810.HK, ^HSI, ETH-USD"))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Verify user credentials. Returns user_id if valid, None otherwise."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    hashed_pw = hash_password(password)
    c.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, hashed_pw))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None

def get_user_watchlist(user_id):
    """Get the watchlist symbols for a user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT symbols FROM watchlists WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return ""

def update_user_watchlist(user_id, symbols):
    """Update the watchlist for a user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Check if watchlist exists, if not create one (should exist from register, but just in case)
    c.execute('SELECT id FROM watchlists WHERE user_id = ?', (user_id,))
    if c.fetchone():
        c.execute('UPDATE watchlists SET symbols = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (symbols, user_id))
    else:
        c.execute('INSERT INTO watchlists (user_id, symbols) VALUES (?, ?)', (user_id, symbols))
        
    conn.commit()
    conn.close()

# Initialize DB on module load if it doesn't exist
if not os.path.exists(DB_FILE):
    init_db()
else:
    # Ensure tables exist even if file exists (e.g. empty file)
    init_db()
