import sqlite3
from pathlib import Path

DB_PATH = Path("newsletter.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    #Subscribers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'active',
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        unsubscribe_token TEXT UNIQUE  
    )                 
    """)
    
    #sends table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        edition_number INTEGER,
        subject TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_recipients INTEGER,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()