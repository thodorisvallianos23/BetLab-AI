import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def create_bankroll_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bankroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        starting_balance REAL NOT NULL,
        current_balance REAL NOT NULL,
        currency TEXT DEFAULT 'EUR'
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM bankroll")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("""
        INSERT INTO bankroll (starting_balance, current_balance, currency)
        VALUES (?, ?, ?)
        """, (1000.0, 1000.0, "EUR"))

    conn.commit()
    conn.close()

    print("✅ Bankroll table created")


if __name__ == "__main__":
    create_bankroll_table()