import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab.db")
CSV_PATH = Path("data/sample_matches.csv")

def import_matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(CSV_PATH, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
            INSERT INTO matches (
                match_date, league, home_team, away_team,
                home_goals, away_goals, home_xg, away_xg,
                home_shots, away_shots, home_sot, away_sot,
                home_corners, away_corners
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["match_date"], row["league"], row["home_team"], row["away_team"],
                int(row["home_goals"]), int(row["away_goals"]),
                float(row["home_xg"]), float(row["away_xg"]),
                int(row["home_shots"]), int(row["away_shots"]),
                int(row["home_sot"]), int(row["away_sot"]),
                int(row["home_corners"]), int(row["away_corners"])
            ))

    conn.commit()
    conn.close()
    print("✅ Matches imported successfully!")

if __name__ == "__main__":
    import_matches()
    