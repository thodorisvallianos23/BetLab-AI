import sqlite3

conn = sqlite3.connect("data/betlab_v2.db")
cur = conn.cursor()

print("MATCH COUNT:", cur.execute(
    "SELECT COUNT(*) FROM matches"
).fetchone()[0])

print("FINISHED:", cur.execute(
    "SELECT COUNT(*) FROM matches WHERE status = 'finished'"
).fetchone()[0])

print("DATE RANGE:", cur.execute(
    "SELECT MIN(match_date), MAX(match_date) FROM matches"
).fetchone())

print("TEAMS:", cur.execute(
    "SELECT COUNT(*) FROM teams"
).fetchone()[0])

print("LEAGUES:", cur.execute(
    "SELECT COUNT(*) FROM leagues"
).fetchone()[0])

conn.close()
