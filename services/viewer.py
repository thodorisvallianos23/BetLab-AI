import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab.db")

def show_matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT match_date, league, home_team, away_team, home_goals, away_goals,
           home_xg, away_xg, home_shots, away_shots
    FROM matches
    """)

    rows = cursor.fetchall()
    conn.close()

    print("\n⚽ BetLab Matches\n")

    for row in rows:
        print(
            f"{row[0]} | {row[1]} | {row[2]} {row[4]}-{row[5]} {row[3]} "
            f"| xG: {row[6]}-{row[7]} | Shots: {row[8]}-{row[9]}"
        )

if __name__ == "__main__":
    show_matches()