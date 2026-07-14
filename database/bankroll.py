import sqlite3
from pathlib import Path


DB_PATH = Path("data/betlab_v2.db")


def create_bankroll_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bankroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            starting_balance REAL NOT NULL,
            current_balance REAL NOT NULL,
            currency TEXT DEFAULT 'EUR'
        )
        """
    )

    cursor.execute("SELECT COUNT(*) FROM bankroll")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            """
            INSERT INTO bankroll (
                starting_balance,
                current_balance,
                currency
            )
            VALUES (?, ?, ?)
            """,
            (1000.0, 1000.0, "EUR"),
        )

    conn.commit()
    conn.close()

    print("✅ Bankroll table created")


def get_bankroll():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            starting_balance,
            current_balance,
            currency
        FROM bankroll
        ORDER BY id ASC
        LIMIT 1
        """
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {
            "starting_balance": 0.0,
            "current_balance": 0.0,
            "currency": "EUR",
        }

    return {
        "starting_balance": float(row[0]),
        "current_balance": float(row[1]),
        "currency": row[2],
    }


def calculate_suggested_stake(quarter_kelly_percent):
    bankroll = get_bankroll()

    current_balance = bankroll["current_balance"]

    stake = current_balance * (
        quarter_kelly_percent / 100
    )

    return round(stake, 2)


if __name__ == "__main__":
    create_bankroll_table()

    bankroll = get_bankroll()

    print("Current bankroll:", bankroll)

    test_stake = calculate_suggested_stake(2.0)

    print("Suggested stake:", test_stake)