import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def get_bookmakers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM bookmakers
        ORDER BY name
    """)

    bookmakers = [row[0] for row in cursor.fetchall()]

    conn.close()

    return bookmakers


def add_bookmaker(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO bookmakers (name)
        VALUES (?)
        """,
        (name,),
    )

    conn.commit()
    conn.close()