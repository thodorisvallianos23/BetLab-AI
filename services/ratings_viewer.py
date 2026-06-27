import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT team_name, attack_rating, defence_rating
FROM teams
ORDER BY attack_rating DESC
""")

print("\n📊 BetLab Team Ratings\n")

for team, attack, defence in cursor.fetchall():
    print(f"{team:20} | ATT: {attack:5.1f} | DEF: {defence:5.1f}")

conn.close()