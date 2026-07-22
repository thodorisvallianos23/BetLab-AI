import sqlite3

DB_PATH = "data/betlab_v2.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\nTABLES")
print("-" * 50)

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
)

tables = cursor.fetchall()

for table in tables:
    print(table[0])

conn.close()