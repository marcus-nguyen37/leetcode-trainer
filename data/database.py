import sqlite3

from constants import DB_NAME

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Problems database storing LeetCode problems metadata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS problems(
        id INTEGER PRIMARY KEY,
        slug TEXT UNIQUE,
        title TEXT,
        difficulty TEXT,
        topics TEXT
    )
    """)

    # Attempts database storing each problem attempt's metadata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attempts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug str UNIQUE,
        date TEXT,
        time_taken INTEGER,
        confidence INTEGER,
        success INTEGER
    )
    """)

    conn.commit()
    conn.close()
