from database.connection import get_connection


def get_team_id(team_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM teams
        WHERE LOWER(team_name) = LOWER(?)
        """,
        (team_name,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return row["id"]

    return None
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