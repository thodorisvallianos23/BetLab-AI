import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def save_bet(bet_date, match_name, market, selection, bookmaker, odds, stake):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO bets (
            bet_date, match_name, market, selection, bookmaker, odds, stake
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (bet_date, match_name, market, selection, bookmaker, odds, stake),
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


def update_bet_result(bet_id, result, profit_loss):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bets
        SET result = ?, profit_loss = ?
        WHERE id = ?
        """,
        (result, profit_loss, bet_id),
    )
def settle_bet(bet_id, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT odds, stake, result
        FROM bets
        WHERE id = ?
    """, (bet_id,))

    bet = cursor.fetchone()

    if not bet:
        conn.close()
        return False

    odds, stake, old_result = bet

    if old_result != "Pending":
        conn.close()
        return False

    if result == "Won":
        profit_loss = stake * (odds - 1)
    elif result == "Lost":
        profit_loss = -stake
    else:
        profit_loss = 0

    cursor.execute("""
        UPDATE bets
        SET result = ?, profit_loss = ?
        WHERE id = ?
    """, (result, profit_loss, bet_id))

    cursor.execute("""
        UPDATE bankroll
        SET current_balance = current_balance + ?
        WHERE id = 1
    """, (profit_loss,))

    conn.commit()
    conn.close()

    return True
    conn.commit()
    conn.close()