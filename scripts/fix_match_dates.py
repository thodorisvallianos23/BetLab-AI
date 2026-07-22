import sqlite3
from datetime import datetime

DB = "data/betlab_v2.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

rows = cur.execute("""
SELECT id, match_date
FROM matches
""").fetchall()

updated = 0

for match_id, date_str in rows:

    if not date_str:
        continue

    try:
        new_date = datetime.strptime(
            date_str,
            "%d/%m/%Y"
        ).strftime("%Y-%m-%d")

        cur.execute("""
        UPDATE matches
        SET match_date = ?
        WHERE id = ?
        """, (new_date, match_id))

        updated += 1

    except Exception:
        print(f"Skipped: {match_id} -> {date_str}")

conn.commit()

print(f"Updated {updated} matches.")

print(
    cur.execute("""
    SELECT MIN(match_date), MAX(match_date)
    FROM matches
    """).fetchone()
)

conn.close()