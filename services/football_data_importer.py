import sqlite3
import pandas as pd
from pathlib import Path

CSV_PATH = Path("data/raw/premier_league_2526.csv")
DB_PATH = Path("data/betlab_v2.db")


def get_or_create(cursor, table, column, value, extra_columns=None):
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
    row = cursor.fetchone()

    if row:
        return row[0]

    if extra_columns:
        columns = [column] + list(extra_columns.keys())
        values = [value] + list(extra_columns.values())
        placeholders = ",".join(["?"] * len(values))

        cursor.execute(
            f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
            values
        )
    else:
        cursor.execute(
            f"INSERT INTO {table} ({column}) VALUES (?)",
            (value,)
        )

    return cursor.lastrowid


def import_football_data():
    df = pd.read_csv(CSV_PATH)
    df = df.dropna(subset=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    league_id = get_or_create(
        cursor,
        "leagues",
        "league_name",
        "Premier League",
        {"country": "England"}
    )

    season_id = get_or_create(
        cursor,
        "seasons",
        "season_name",
        "2025/26"
    )

    imported = 0

    for _, row in df.iterrows():
        home_team_id = get_or_create(cursor, "teams", "team_name", row["HomeTeam"])
        away_team_id = get_or_create(cursor, "teams", "team_name", row["AwayTeam"])

        cursor.execute("""
        INSERT INTO matches (
            match_date, league_id, season_id,
            home_team_id, away_team_id,
            home_goals, away_goals, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["Date"],
            league_id,
            season_id,
            home_team_id,
            away_team_id,
            int(row["FTHG"]),
            int(row["FTAG"]),
            "finished"
        ))

        imported += 1

    conn.commit()
    conn.close()

    print(f"✅ Imported {imported} matches into BetLab v2")


if __name__ == "__main__":
    import_football_data()