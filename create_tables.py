# create_tables.py
import sqlite3

DB = "database3.db"

conn = sqlite3.connect(DB)
c = conn.cursor()

# users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    user_code TEXT UNIQUE NOT NULL
)
''')

# records table
c.execute('''

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    production_order TEXT,
    quantity INTEGER,
    deburring INTEGER DEFAULT 0,
    deburring_qty INTEGER,
    sorting INTEGER DEFAULT 0,
    sorting_qty INTEGER,
    waste_disposal INTEGER DEFAULT 0,
    waste_qty INTEGER,
    start_time TEXT,
    finish_time TEXT,
    non_order INTEGER DEFAULT 0,
    causale TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
''')

# Insert test user Marco Palla code 222 if not exists
c.execute("SELECT id FROM users WHERE user_code = ?", ("222",))
if not c.fetchone():
    c.execute("INSERT INTO users (first_name, last_name, user_code) VALUES (?, ?, ?)",
              ("Marco", "Palla", "222"))
    print("Inserted test user Marco Palla (code 222).")

conn.commit()
conn.close()
print("Database initialized (database.db).")
