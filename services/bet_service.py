import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def save_bet(
    bet_date,
    match_name,
    market,
    selection,
    bookmaker,
    odds,
    stake,
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO bets
        (
            bet_date,
            match_name,
            market,
            selection,
            bookmaker,
            odds,
            stake
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            bet_date,
            match_name,
            market,
            selection,
            bookmaker,
            odds,
            stake,
        ),
    )

    conn.commit()
    conn.close()


def get_all_bets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM bets
        ORDER BY id DESC
    """)

    bets = cursor.fetchall()

    conn.close()

    return bets