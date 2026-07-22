import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")

TEAM_NAME = input("Enter team name: ")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT team_name
FROM teams
ORDER BY team_name
""")

for row in cursor.fetchall():
    print(row[0])

conn.close()

team = cursor.fetchone()

if not team:
    print("❌ Team not found")
    exit()

cursor.execute("""
SELECT
    COUNT(*),
    SUM(home_goals + away_goals)
FROM matches
WHERE home_team_id = (
    SELECT id FROM teams WHERE team_name = ?
)
OR away_team_id = (
    SELECT id FROM teams WHERE team_name = ?
)
""", (TEAM_NAME, TEAM_NAME))

matches, total_goals = cursor.fetchone()

print("\n==============================")
print(f"🏆 {team[0]}")
print("==============================")
print(f"Matches: {matches}")
print(f"Goals in matches: {total_goals}")
print(f"Attack Rating: {team[1]:.1f}")
print(f"Defence Rating: {team[2]:.1f}")

conn.close()