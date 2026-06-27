import sqlite3
from pathlib import Path
import sys
def fair_odds(probability):
    if probability <= 0:
        return None
    return 1 / probability
sys.path.append(str(Path(__file__).resolve().parent))

from poisson import over_probability

DB_PATH = Path("data/betlab_v2.db")


def predict_match(home_team, away_team):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT team_name, attack_rating, defence_rating
        FROM teams
        WHERE team_name IN (?, ?)
    """, (home_team, away_team))

    data = {row[0]: row for row in cursor.fetchall()}
    conn.close()

    if home_team not in data or away_team not in data:
        print("❌ Team not found in database")
        return

    home_attack = data[home_team][1]
    home_defence = data[home_team][2]
    away_attack = data[away_team][1]
    away_defence = data[away_team][2]

    home_xg = max(0.2, (home_attack / 50) * (100 - away_defence) / 50 + 0.35)
    away_xg = max(0.2, (away_attack / 50) * (100 - home_defence) / 50)

    total_xg = home_xg + away_xg

    print(f"\n⚽ Prediction: {home_team} vs {away_team}\n")
    print(f"Home xG: {home_xg:.2f}")
    print(f"Away xG: {away_xg:.2f}")
    print(f"Total xG: {total_xg:.2f}")
    for line in [1.5, 2.5, 3.5]:
        prob = over_probability(total_xg, line)
        odds = fair_odds(prob)

    print(
        f"Over {line}: {prob * 100:.2f}% | "
        f"Fair Odds: {odds:.2f}"
    )

if __name__ == "__main__":
    home = input("Enter home team: ")
    away = input("Enter away team: ")
    predict_match(home, away)