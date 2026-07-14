import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def bet_already_exists(
    bet_date,
    match_name,
    market,
    bookmaker,
    odds,
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM bets
        WHERE bet_date = ?
          AND match_name = ?
          AND market = ?
          AND bookmaker = ?
          AND odds = ?
          AND result = 'Pending'
        LIMIT 1
        """,
        (
            bet_date,
            match_name,
            market,
            bookmaker,
            odds,
        ),
    )

    exists = cursor.fetchone() is not None
    conn.close()

    return exists


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
        INSERT INTO bets (
            bet_date,
            match_name,
            market,
            selection,
            bookmaker,
            odds,
            stake,
            result,
            profit_loss
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            bet_date,
            match_name,
            market,
            selection,
            bookmaker,
            odds,
            stake,
            "Pending",
            0.0,
        ),
    )

    conn.commit()
    conn.close()


def get_all_bets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bets
        ORDER BY id DESC
        """
    )

    bets = cursor.fetchall()
    conn.close()

    return bets


def update_bet_result(bet_id, result, profit_loss):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bets
        SET result = ?,
            profit_loss = ?
        WHERE id = ?
        """,
        (
            result,
            profit_loss,
            bet_id,
        ),
    )

    conn.commit()
    conn.close()


def settle_bet(bet_id, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT odds, stake, result
        FROM bets
        WHERE id = ?
        """,
        (bet_id,),
    )

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
    elif result == "Push":
        profit_loss = 0.0
    else:
        conn.close()
        return False

    cursor.execute(
        """
        UPDATE bets
        SET result = ?,
            profit_loss = ?
        WHERE id = ?
        """,
        (
            result,
            profit_loss,
            bet_id,
        ),
    )

    cursor.execute(
        """
        UPDATE bankroll
        SET current_balance = current_balance + ?
        WHERE id = 1
        """,
        (profit_loss,),
    )

    conn.commit()
    conn.close()

    return True


def update_bet(
    bet_id,
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
        UPDATE bets
        SET bet_date = ?,
            match_name = ?,
            market = ?,
            selection = ?,
            bookmaker = ?,
            odds = ?,
            stake = ?
        WHERE id = ?
        """,
        (
            bet_date,
            match_name,
            market,
            selection,
            bookmaker,
            odds,
            stake,
            bet_id,
        ),
    )

    updated = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return updated


def delete_bet(bet_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT result, profit_loss
        FROM bets
        WHERE id = ?
        """,
        (bet_id,),
    )

    bet = cursor.fetchone()

    if not bet:
        conn.close()
        return False

    result, profit_loss = bet

    if result != "Pending":
        cursor.execute(
            """
            UPDATE bankroll
            SET current_balance = current_balance - ?
            WHERE id = 1
            """,
            (profit_loss,),
        )

    cursor.execute(
        """
        DELETE FROM bets
        WHERE id = ?
        """,
        (bet_id,),
    )

    conn.commit()
    conn.close()

    return True