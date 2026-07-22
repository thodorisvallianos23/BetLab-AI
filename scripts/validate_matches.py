import sqlite3

DB = "data/betlab_v2.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

total = cur.execute(
    "SELECT COUNT(*) FROM matches"
).fetchone()[0]

invalid_dates = cur.execute("""
SELECT COUNT(*)
FROM matches
WHERE match_date IS NULL
   OR match_date NOT GLOB '????-??-??'
""").fetchone()[0]

missing_teams = cur.execute("""
SELECT COUNT(*)
FROM matches
WHERE home_team_id IS NULL
   OR away_team_id IS NULL
""").fetchone()[0]

missing_scores = cur.execute("""
SELECT COUNT(*)
FROM matches
WHERE status = 'finished'
  AND (
      home_goals IS NULL
      OR away_goals IS NULL
  )
""").fetchone()[0]

duplicate_matches = cur.execute("""
SELECT COUNT(*)
FROM (
    SELECT
        match_date,
        home_team_id,
        away_team_id,
        COUNT(*) AS occurrences
    FROM matches
    GROUP BY
        match_date,
        home_team_id,
        away_team_id
    HAVING COUNT(*) > 1
)
""").fetchone()[0]

print("TOTAL MATCHES:", total)
print("INVALID DATES:", invalid_dates)
print("MISSING TEAMS:", missing_teams)
print("MISSING FINISHED SCORES:", missing_scores)
print("DUPLICATE FIXTURES:", duplicate_matches)

print("\nLATEST 5 MATCHES:")

rows = cur.execute("""
SELECT
    m.match_date,
    h.team_name,
    a.team_name,
    m.home_goals,
    m.away_goals
FROM matches AS m
LEFT JOIN teams AS h
    ON h.id = m.home_team_id
LEFT JOIN teams AS a
    ON a.id = m.away_team_id
ORDER BY m.match_date DESC
LIMIT 5
""").fetchall()

for row in rows:
    print(row)

conn.close()