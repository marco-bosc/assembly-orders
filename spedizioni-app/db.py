
# db.py
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "shipments.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Tabella spedizioni
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ddt TEXT NOT NULL,
        tracking TEXT NOT NULL,
        courier TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_deleted INTEGER NOT NULL DEFAULT 0,
        deleted_at TIMESTAMP NULL
    )
    """)

    # Set "prima volta stampata" (unique per parcel)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS printed_labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parcel_id TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Audit di tutte le scansioni
    cur.execute("""
    CREATE TABLE IF NOT EXISTS printed_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parcel_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn
