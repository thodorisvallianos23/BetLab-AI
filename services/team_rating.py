import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def calculate_team_ratings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, team_name
        FROM teams
        ORDER BY team_name
    """)

    teams = cursor.fetchall()

    print("\n🏆 BETLAB TEAM RATINGS\n")
    print("-" * 70)

    for team_id, team_name in teams:

        # Εντός έδρας
        cursor.execute("""
            SELECT
                COUNT(*),
                AVG(home_goals),
                AVG(away_goals)
            FROM matches
            WHERE home_team_id = ?
        """, (team_id,))

        home_matches, avg_home_goals, avg_home_conceded = cursor.fetchone()

        # Εκτός έδρας
        cursor.execute("""
            SELECT
                COUNT(*),
                AVG(away_goals),
                AVG(home_goals)
            FROM matches
            WHERE away_team_id = ?
        """, (team_id,))

        away_matches, avg_away_goals, avg_away_conceded = cursor.fetchone()

        total_matches = (home_matches or 0) + (away_matches or 0)

        if total_matches == 0:
            continue

        goals_for = (
            ((avg_home_goals or 0) * (home_matches or 0)) +
            ((avg_away_goals or 0) * (away_matches or 0))
        ) / total_matches

        goals_against = (
            ((avg_home_conceded or 0) * (home_matches or 0)) +
            ((avg_away_conceded or 0) * (away_matches or 0))
        ) / total_matches

        attack_rating = round(goals_for * 25, 1)
        defence_rating = round(max(0, 100 - goals_against * 25), 1)

        print(
            f"{team_name:20} | "
            f"Matches: {total_matches:3} | "
            f"GF: {goals_for:.2f} | "
            f"GA: {goals_against:.2f} | "
            f"ATT: {attack_rating:5} | "
            f"DEF: {defence_rating:5}"
        )
        cursor.execute("""
            UPDATE teams
            SET attack_rating = ?, defence_rating = ?
            WHERE id = ?
        """, (attack_rating, defence_rating, team_id))
   
        conn.commit()
    print("\n✅ Team ratings saved to database")
    conn.close()


if __name__ == "__main__":
    calculate_team_ratings()