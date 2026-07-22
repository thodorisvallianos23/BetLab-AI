import sqlite3

DB_PATH = "data/betlab_v2.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for table_name in ("teams", "seasons"):
    print()
    print(f"{table_name.upper()} TABLE")
    print("-" * 60)

    cursor.execute(f"PRAGMA table_info({table_name});")

    for column in cursor.fetchall():
        print(column)

print()
print("SAMPLE MATCHES")
print("-" * 60)

cursor.execute(
    """
    SELECT *
    FROM matches
    ORDER BY match_date
    LIMIT 5;
    """
)

for row in cursor.fetchall():
    print(row)

conn.close()
