from database.connection import get_connection


import re
import unicodedata

TEAM_SUFFIXES = {
    "fc",
    "cf",
    "afc",
    "ac",
    "sc",
    "ssc",
}


def normalize_team_key(team_name):
    normalized = unicodedata.normalize(
        "NFKD",
        team_name,
    )

    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.lower()
    normalized = re.sub(
        r"[^a-z0-9\s]",
        " ",
        normalized,
    )

    words = normalized.split()

    while words and words[-1] in TEAM_SUFFIXES:
        words.pop()

    return " ".join(words)


def get_team_id(team_name):
    target_key = normalize_team_key(team_name)
    
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id, team_name
            FROM teams
            """
        )

        for row in cursor.fetchall():
            if normalize_team_key(row["team_name"]) == target_key:
                return row["id"]

        return None

    finally:
        connection.close()


def get_league_id(league_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM leagues
        WHERE LOWER(league_name) = LOWER(?)
        """,
        (league_name,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return row["id"]

    return None


def get_season_id(season_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM seasons
        WHERE LOWER(season_name) = LOWER(?)
        """,
        (season_name,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return row["id"]

    return None