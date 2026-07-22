from database.connection import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
SELECT id, team_name
FROM teams
ORDER BY team_name
""")

teams = cursor.fetchall()

print(f"\nTotal teams: {len(teams)}\n")

seen = {}

for team in teams:
    name = (
        team["team_name"]
        .replace(" FC", "")
        .replace(" AFC", "")
        .replace(" CF", "")
        .strip()
        .lower()
    )

    seen.setdefault(name, []).append(team)

duplicates = False

for _, rows in sorted(seen.items()):
    if len(rows) > 1:
        duplicates = True
        print("-" * 60)
        for row in rows:
            print(f'{row["id"]:4}  {row["team_name"]}')

if not duplicates:
    print("✅ No duplicate teams found.")

connection.close()