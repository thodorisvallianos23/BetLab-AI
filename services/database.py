import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab.db")

def create_database():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_date TEXT,
        league TEXT,
        home_team TEXT,
        away_team TEXT,
        home_goals INTEGER,
        away_goals INTEGER,
        home_xg REAL,
        away_xg REAL,
        home_shots INTEGER,
        away_shots INTEGER,
        home_sot INTEGER,
        away_sot INTEGER,
        home_corners INTEGER,
        away_corners INTEGER
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database created successfully!")

if __name__ == "__main__":
    create_database()
    