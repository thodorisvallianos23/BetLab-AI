import sqlite3
from pathlib import Path
from poisson import over_probability

DB_PATH = Path("data/betlab.db")

def run_goal_engine():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT home_team, away_team, home_xg, away_xg
    FROM matches
    """)

    matches = cursor.fetchall()
    conn.close()

    print("\n⚽ BetLab Goal Engine\n")

    for home, away, home_xg, away_xg in matches:
        total_xg = home_xg + away_xg

        over_05 = over_probability(total_xg, 0.5) * 100
        over_15 = over_probability(total_xg, 1.5) * 100
        over_25 = over_probability(total_xg, 2.5) * 100
        over_35 = over_probability(total_xg, 3.5) * 100

        print(f"{home} vs {away}")
        print(f"Total xG: {round(total_xg, 2)}")
        print(f"Over 0.5: {round(over_05, 2)}%")
        print(f"Over 1.5: {round(over_15, 2)}%")
        print(f"Over 2.5: {round(over_25, 2)}%")
        print(f"Over 3.5: {round(over_35, 2)}%")
        print("-" * 40)

if __name__ == "__main__":
    run_goal_engine()
    