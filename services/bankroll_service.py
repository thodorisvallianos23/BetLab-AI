import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def get_bankroll():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT starting_balance, current_balance, currency
        FROM bankroll
        LIMIT 1
    """)

    bankroll = cursor.fetchone()
    conn.close()

    return bankroll


def update_balance(new_balance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bankroll
        SET current_balance = ?
        WHERE id = 1
    """, (new_balance,))

    conn.commit()
    conn.close()


def set_starting_balance(balance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bankroll
        SET starting_balance = ?, current_balance = ?
        WHERE id = 1
    """, (balance, balance))

    conn.commit()
    conn.close()