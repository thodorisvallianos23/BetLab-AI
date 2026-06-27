import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab.db")

def calculate_team_features():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT home_team, home_xg, home_shots, home_sot, home_corners
    FROM matches
    """)

    rows = cursor.fetchall()
    conn.close()

    print("\n📊 Team Feature Engine\n")

    for team, xg, shots, sot, corners in rows:
        attack_score = (xg * 30) + (shots * 2) + (sot * 4) + (corners * 1.5)

        print(
            f"{team} | xG: {xg} | Shots: {shots} | SOT: {sot} | "
            f"Corners: {corners} | Attack Score: {round(attack_score, 2)}"
        )

if __name__ == "__main__":
    calculate_team_features()
    