from database.connection import get_connection
from services.football_api import get_competition_matches


def get_or_create(
    cursor,
    table,
    column,
    value,
    extra_columns=None,
):
    cursor.execute(
        f"SELECT id FROM {table} WHERE {column} = ?",
        (value,),
    )

    row = cursor.fetchone()

    if row:
        return row["id"]

    extra_columns = extra_columns or {}

    columns = [column] + list(extra_columns.keys())
    values = [value] + list(extra_columns.values())
    placeholders = ", ".join(["?"] * len(values))

    cursor.execute(
        f"""
        INSERT INTO {table} ({", ".join(columns)})
        VALUES ({placeholders})
        """,
        values,
    )

    return cursor.lastrowid


def build_season_name(match, fallback_season=None):
    season_start = match.get("season_start")
    season_end = match.get("season_end")

    if season_start and season_end:
        start_year = season_start[:4]
        end_year = season_end[:4]
        return f"{start_year}/{end_year}"

    if fallback_season is not None:
        return f"{fallback_season}/{fallback_season + 1}"

    return "Unknown"


def match_exists(
    cursor,
    match_date,
    league_id,
    home_team_id,
    away_team_id,
):
    cursor.execute(
        """
        SELECT id
        FROM matches
        WHERE match_date = ?
          AND league_id = ?
          AND home_team_id = ?
          AND away_team_id = ?
        LIMIT 1
        """,
        (
            match_date,
            league_id,
            home_team_id,
            away_team_id,
        ),
    )

    return cursor.fetchone() is not None


def import_league(
    competition_code,
    season=None,
):
    print(f"\n===== IMPORTING {competition_code} =====")

    matches = get_competition_matches(
        competition_code,
        season,
    )

    if not matches:
        print("❌ No matches returned.")
        return {
            "downloaded": 0,
            "inserted": 0,
            "skipped": 0,
        }

    connection = get_connection()
    cursor = connection.cursor()

    inserted_matches = 0
    skipped_matches = 0

    try:
        print(f"Downloaded {len(matches)} matches.")

        for match in matches:
            league_name = match.get("league_name")
            country = match.get("country")
            match_date = match.get("match_date")
            home_team = match.get("home_team")
            away_team = match.get("away_team")
            home_goals = match.get("home_goals")
            away_goals = match.get("away_goals")
            status = match.get("status") or "scheduled"

            if not all(
                [
                    league_name,
                    match_date,
                    home_team,
                    away_team,
                ]
            ):
                skipped_matches += 1
                continue

            season_name = build_season_name(
                match,
                fallback_season=season,
            )

            league_id = get_or_create(
                cursor,
                table="leagues",
                column="league_name",
                value=league_name,
                extra_columns={
                    "country": country,
                },
            )

            season_id = get_or_create(
                cursor,
                table="seasons",
                column="season_name",
                value=season_name,
            )

            home_team_id = get_or_create(
                cursor,
                table="teams",
                column="team_name",
                value=home_team,
                extra_columns={
                    "country": country,
                    "league": league_name,
                },
            )

            away_team_id = get_or_create(
                cursor,
                table="teams",
                column="team_name",
                value=away_team,
                extra_columns={
                    "country": country,
                    "league": league_name,
                },
            )

            if match_exists(
                cursor,
                match_date=match_date,
                league_id=league_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
            ):
                skipped_matches += 1
                continue

            cursor.execute(
                """
                INSERT INTO matches (
                    match_date,
                    league_id,
                    season_id,
                    home_team_id,
                    away_team_id,
                    home_goals,
                    away_goals,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    match_date,
                    league_id,
                    season_id,
                    home_team_id,
                    away_team_id,
                    home_goals,
                    away_goals,
                    status,
                ),
            )

            inserted_matches += 1

        connection.commit()

        print()
        print("===== IMPORT COMPLETE =====")
        print(f"Downloaded: {len(matches)}")
        print(f"Inserted:   {inserted_matches}")
        print(f"Skipped:    {skipped_matches}")

        return {
            "downloaded": len(matches),
            "inserted": inserted_matches,
            "skipped": skipped_matches,
        }

    except Exception as error:
        connection.rollback()
        print(f"❌ Import failed: {error}")
        raise

    finally:
        connection.close()