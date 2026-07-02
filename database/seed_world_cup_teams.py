import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")

TEAMS = [
    ("United States", 74, 70),
    ("Bosnia-Herzegovina", 68, 66),
    ("Spain", 88, 84),
    ("Austria", 76, 74),
    ("Portugal", 86, 82),
    ("Croatia", 80, 78),
    ("Switzerland", 76, 76),
    ("Algeria", 72, 70),
    ("Australia", 68, 68),
    ("Egypt", 74, 70),
    ("Argentina", 90, 84),
    ("Cape Verde Islands", 64, 62),
    ("Colombia", 78, 74),
    ("Ghana", 70, 68),
    ("Canada", 72, 68),
    ("Morocco", 78, 76),
    ("Paraguay", 70, 70),
    ("France", 90, 86),
    ("Brazil", 90, 82),
    ("Norway", 78, 72),
    ("Mexico", 76, 72),
    ("England", 88, 84),
    ("Belgium", 82, 78),
]

def seed_world_cup_teams():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for team_name, attack_rating, defence_rating in TEAMS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO teams (team_name, attack_rating, defence_rating)
            VALUES (?, ?, ?)
            """,
            (team_name, attack_rating, defence_rating),
        )

    conn.commit()
    conn.close()

    print("✅ World Cup teams seeded")


if __name__ == "__main__":
    seed_world_cup_teams()