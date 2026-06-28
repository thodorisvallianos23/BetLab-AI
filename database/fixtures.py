import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def create_fixtures_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fixtures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fixture_date TEXT NOT NULL,
        league TEXT,
        home_team TEXT NOT NULL,
        away_team TEXT NOT NULL,
        status TEXT DEFAULT 'upcoming'
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Fixtures table created")


if __name__ == "__main__":
    create_fixtures_table()