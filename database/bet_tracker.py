import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def create_bet_tracker_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bet_date TEXT,
        match_name TEXT,
        market TEXT,
        selection TEXT,
        bookmaker TEXT,
        odds REAL,
        stake REAL,
        result TEXT DEFAULT 'Pending',
        profit_loss REAL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Bet tracker table created")


if __name__ == "__main__":
    create_bet_tracker_table()