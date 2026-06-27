import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n📊 BetLab Database Check\n")

tables = ["leagues", "seasons", "teams", "matches"]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count}")

print("\n🏆 Πρώτοι 10 αγώνες:\n")

cursor.execute("""
SELECT
    m.match_date,
    ht.team_name,
    at.team_name,
    m.home_goals,
    m.away_goals
FROM matches m
JOIN teams ht ON ht.id = m.home_team_id
JOIN teams at ON at.id = m.away_team_id
LIMIT 10;
""")

for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} {row[3]}-{row[4]} {row[2]}")

conn.close()