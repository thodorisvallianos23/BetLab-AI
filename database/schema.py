import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")

def create_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leagues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        league_name TEXT UNIQUE NOT NULL,
        country TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seasons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        season_name TEXT UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT UNIQUE NOT NULL,
        country TEXT,
        league TEXT,
        elo_rating REAL DEFAULT 1500,
        attack_rating REAL DEFAULT 50,
        defence_rating REAL DEFAULT 50
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_date TEXT NOT NULL,
        league_id INTEGER,
        season_id INTEGER,
        home_team_id INTEGER,
        away_team_id INTEGER,
        home_goals INTEGER,
        away_goals INTEGER,
        status TEXT DEFAULT 'finished',
        FOREIGN KEY (league_id) REFERENCES leagues(id),
        FOREIGN KEY (season_id) REFERENCES seasons(id),
        FOREIGN KEY (home_team_id) REFERENCES teams(id),
        FOREIGN KEY (away_team_id) REFERENCES teams(id)
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database v2 schema created successfully")

if __name__ == "__main__":
    create_schema()