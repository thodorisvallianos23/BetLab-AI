import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def create_bookmakers_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmakers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    default_bookmakers = [
        "Bet365",
        "Stoiximan",
        "Novibet",
        "Betsson",
        "Fonbet",
    ]

    for bookmaker in default_bookmakers:
        cursor.execute(
            "INSERT OR IGNORE INTO bookmakers (name) VALUES (?)",
            (bookmaker,),
        )

    conn.commit()
    conn.close()

    print("✅ Bookmakers table created")


if __name__ == "__main__":
    create_bookmakers_table()