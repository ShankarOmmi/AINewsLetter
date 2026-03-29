import sqlite3
from pathlib import Path
from config import DATABASE_URL
from utils.logger import logger

# Determine if using PostgreSQL or SQLite
IS_POSTGRES = DATABASE_URL and "postgresql" in DATABASE_URL
DB_PATH = Path("newsletter.db")

def get_connection():
    """Get database connection - PostgreSQL or SQLite based on DATABASE_URL"""
    if IS_POSTGRES:
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except ImportError:
            logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {str(e)}")
            raise
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def create_tables():
    """Create tables for both PostgreSQL and SQLite"""
    if IS_POSTGRES:
        create_postgres_tables()
    else:
        create_sqlite_tables()

def create_sqlite_tables():
    """Create SQLite tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Subscribers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'active',
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        unsubscribe_token TEXT UNIQUE  
    )                 
    """)
    
    # Sends table
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

    # Editions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS editions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        content TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def create_postgres_tables():
    """Create PostgreSQL tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Subscribers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers(
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'active',
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        unsubscribe_token TEXT UNIQUE  
    )
    """)
    
    # Sends table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sends (
        id SERIAL PRIMARY KEY,
        edition_number INTEGER,
        subject TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_recipients INTEGER,
        status TEXT
    )
    """)

    # Editions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS editions (
        id SERIAL PRIMARY KEY,
        subject TEXT,
        content TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    logger.info("PostgreSQL tables created")