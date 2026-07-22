import sqlite3
from dataclasses import dataclass
from typing import Optional


DB_PATH = "data/betlab_v2.db"


@dataclass
class LeagueAverages:
    matches: int
    home_goals_per_match: float
    away_goals_per_match: float
    total_goals_per_match: float


@dataclass
class TeamRatings:
    team_id: int
    team_name: str
    matches: int

    home_matches: int
    away_matches: int

    home_goals_for_avg: float
    home_goals_against_avg: float
    away_goals_for_avg: float
    away_goals_against_avg: float

    home_attack_strength: float
    home_defence_strength: float
    away_attack_strength: float
    away_defence_strength: float

    recent_form_points: int
    recent_form_score: float


def safe_divide(
    value: float,
    divisor: float,
    default: float = 1.0,
) -> float:
    """Αποφεύγει division by zero."""
    if divisor == 0:
        return default

    return value / divisor


def build_date_filter(
    before_date: Optional[str],
    table_alias: str = "m",
) -> tuple[str, list]:
    """
    Δημιουργεί φίλτρο ημερομηνίας.

    Το before_date αποτρέπει το data leakage,
    επειδή αποκλείει αγώνες από την ημερομηνία
    πρόβλεψης και μετά.
    """
    if before_date:
        return (
            f" AND {table_alias}.match_date < ?",
            [before_date],
        )

    return "", []


def get_league_averages(
    conn: sqlite3.Connection,
    league_id: int,
    season_id: int,
    before_date: Optional[str] = None,
) -> LeagueAverages:
    """
    Υπολογίζει τους μέσους όρους της λίγκας
    για συγκεκριμένη σεζόν.
    """
    date_filter, date_params = build_date_filter(
        before_date
    )

    row = conn.execute(
        f"""
        SELECT
            COUNT(*) AS matches,
            AVG(m.home_goals) AS avg_home_goals,
            AVG(m.away_goals) AS avg_away_goals
        FROM matches AS m
        WHERE m.league_id = ?
          AND m.season_id = ?
          AND LOWER(m.status) = 'finished'
          AND m.home_goals IS NOT NULL
          AND m.away_goals IS NOT NULL
          {date_filter}
        """,
        [
            league_id,
            season_id,
            *date_params,
        ],
    ).fetchone()

    matches = int(row[0] or 0)
    home_avg = float(row[1] or 0.0)
    away_avg = float(row[2] or 0.0)

    return LeagueAverages(
        matches=matches,
        home_goals_per_match=home_avg,
        away_goals_per_match=away_avg,
        total_goals_per_match=home_avg + away_avg,
    )


def get_recent_form(
    conn: sqlite3.Connection,
    team_id: int,
    league_id: int,
    season_id: int,
    number_of_matches: int = 5,
    before_date: Optional[str] = None,
) -> tuple[int, float]:
    """
    Υπολογίζει τη φόρμα μόνο μέσα στη συγκεκριμένη σεζόν.

    Επιστρέφει:
    - συνολικούς βαθμούς,
    - σκορ φόρμας από 0 έως 10.
    """
    if number_of_matches <= 0:
        raise ValueError(
            "number_of_matches must be greater than zero."
        )

    date_filter, date_params = build_date_filter(
        before_date
    )

    rows = conn.execute(
        f"""
        SELECT
            m.home_team_id,
            m.away_team_id,
            m.home_goals,
            m.away_goals
        FROM matches AS m
        WHERE m.league_id = ?
          AND m.season_id = ?
          AND LOWER(m.status) = 'finished'
          AND m.home_goals IS NOT NULL
          AND m.away_goals IS NOT NULL
          AND (
              m.home_team_id = ?
              OR m.away_team_id = ?
          )
          {date_filter}
        ORDER BY
            m.match_date DESC,
            m.id DESC
        LIMIT ?
        """,
        [
            league_id,
            season_id,
            team_id,
            team_id,
            *date_params,
            number_of_matches,
        ],
    ).fetchall()

    points = 0

    for (
        home_team_id,
        away_team_id,
        home_goals,
        away_goals,
    ) in rows:
        if home_goals == away_goals:
            points += 1

        elif (
            home_team_id == team_id
            and home_goals > away_goals
        ):
            points += 3

        elif (
            away_team_id == team_id
            and away_goals > home_goals
        ):
            points += 3

    maximum_points = len(rows) * 3

    if maximum_points == 0:
        return 0, 0.0

    form_score = (
        points / maximum_points
    ) * 10.0

    return points, form_score


def get_team_ratings(
    conn: sqlite3.Connection,
    team_id: int,
    league_id: int,
    season_id: int,
    before_date: Optional[str] = None,
    recent_matches: int = 5,
) -> TeamRatings:
    """
    Υπολογίζει ratings ομάδας για συγκεκριμένη λίγκα,
    συγκεκριμένη σεζόν και προαιρετικά πριν από ημερομηνία.
    """
    league = get_league_averages(
        conn=conn,
        league_id=league_id,
        season_id=season_id,
        before_date=before_date,
    )

    if league.matches == 0:
        raise ValueError(
            "No finished league matches are available "
            "for the selected season and date."
        )

    date_filter, date_params = build_date_filter(
        before_date
    )

    team_row = conn.execute(
        """
        SELECT team_name
        FROM teams
        WHERE id = ?
        """,
        (team_id,),
    ).fetchone()

    if not team_row:
        raise ValueError(
            f"Team ID {team_id} not found."
        )

    team_name = team_row[0]

    home_row = conn.execute(
        f"""
        SELECT
            COUNT(*) AS matches,
            AVG(m.home_goals) AS goals_for,
            AVG(m.away_goals) AS goals_against
        FROM matches AS m
        WHERE m.league_id = ?
          AND m.season_id = ?
          AND m.home_team_id = ?
          AND LOWER(m.status) = 'finished'
          AND m.home_goals IS NOT NULL
          AND m.away_goals IS NOT NULL
          {date_filter}
        """,
        [
            league_id,
            season_id,
            team_id,
            *date_params,
        ],
    ).fetchone()

    away_row = conn.execute(
        f"""
        SELECT
            COUNT(*) AS matches,
            AVG(m.away_goals) AS goals_for,
            AVG(m.home_goals) AS goals_against
        FROM matches AS m
        WHERE m.league_id = ?
          AND m.season_id = ?
          AND m.away_team_id = ?
          AND LOWER(m.status) = 'finished'
          AND m.home_goals IS NOT NULL
          AND m.away_goals IS NOT NULL
          {date_filter}
        """,
        [
            league_id,
            season_id,
            team_id,
            *date_params,
        ],
    ).fetchone()

    home_matches = int(home_row[0] or 0)
    away_matches = int(away_row[0] or 0)

    home_goals_for_avg = float(
        home_row[1] or 0.0
    )
    home_goals_against_avg = float(
        home_row[2] or 0.0
    )

    away_goals_for_avg = float(
        away_row[1] or 0.0
    )
    away_goals_against_avg = float(
        away_row[2] or 0.0
    )

    home_attack_strength = safe_divide(
        home_goals_for_avg,
        league.home_goals_per_match,
    )

    home_defence_strength = safe_divide(
        home_goals_against_avg,
        league.away_goals_per_match,
    )

    away_attack_strength = safe_divide(
        away_goals_for_avg,
        league.away_goals_per_match,
    )

    away_defence_strength = safe_divide(
        away_goals_against_avg,
        league.home_goals_per_match,
    )

    recent_form_points, recent_form_score = (
        get_recent_form(
            conn=conn,
            team_id=team_id,
            league_id=league_id,
            season_id=season_id,
            number_of_matches=recent_matches,
            before_date=before_date,
        )
    )

    return TeamRatings(
        team_id=team_id,
        team_name=team_name,
        matches=home_matches + away_matches,
        home_matches=home_matches,
        away_matches=away_matches,
        home_goals_for_avg=home_goals_for_avg,
        home_goals_against_avg=home_goals_against_avg,
        away_goals_for_avg=away_goals_for_avg,
        away_goals_against_avg=away_goals_against_avg,
        home_attack_strength=home_attack_strength,
        home_defence_strength=home_defence_strength,
        away_attack_strength=away_attack_strength,
        away_defence_strength=away_defence_strength,
        recent_form_points=recent_form_points,
        recent_form_score=recent_form_score,
    )


def print_team_ratings(
    ratings: TeamRatings,
) -> None:
    print(f"\nTEAM: {ratings.team_name}")
    print("-" * 45)

    print(
        f"Matches:                  "
        f"{ratings.matches}"
    )
    print(
        f"Home matches:             "
        f"{ratings.home_matches}"
    )
    print(
        f"Away matches:             "
        f"{ratings.away_matches}"
    )

    print()
    print(
        f"Home goals scored avg:    "
        f"{ratings.home_goals_for_avg:.2f}"
    )
    print(
        f"Home goals conceded avg:  "
        f"{ratings.home_goals_against_avg:.2f}"
    )
    print(
        f"Away goals scored avg:    "
        f"{ratings.away_goals_for_avg:.2f}"
    )
    print(
        f"Away goals conceded avg:  "
        f"{ratings.away_goals_against_avg:.2f}"
    )

    print()
    print(
        f"Home attack strength:     "
        f"{ratings.home_attack_strength:.3f}"
    )
    print(
        f"Home defence strength:    "
        f"{ratings.home_defence_strength:.3f}"
    )
    print(
        f"Away attack strength:     "
        f"{ratings.away_attack_strength:.3f}"
    )
    print(
        f"Away defence strength:    "
        f"{ratings.away_defence_strength:.3f}"
    )

    print()
    print(
        f"Recent form points:       "
        f"{ratings.recent_form_points}"
    )
    print(
        f"Recent form score:        "
        f"{ratings.recent_form_score:.2f}/10"
    )


def main() -> None:
    conn = sqlite3.connect(DB_PATH)

    try:
        league_row = conn.execute(
            """
            SELECT id
            FROM leagues
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()

        season_row = conn.execute(
            """
            SELECT id, season_name
            FROM seasons
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        if not league_row:
            raise ValueError(
                "No league found in database."
            )

        if not season_row:
            raise ValueError(
                "No season found in database."
            )

        league_id = league_row[0]
        season_id = season_row[0]
        season_name = season_row[1]

        league = get_league_averages(
            conn=conn,
            league_id=league_id,
            season_id=season_id,
        )

        print()
        print(f"SEASON: {season_name}")
        print("LEAGUE AVERAGES")
        print("-" * 45)

        print(
            f"Matches:                  "
            f"{league.matches}"
        )
        print(
            f"Home goals per match:     "
            f"{league.home_goals_per_match:.3f}"
        )
        print(
            f"Away goals per match:     "
            f"{league.away_goals_per_match:.3f}"
        )
        print(
            f"Total goals per match:    "
            f"{league.total_goals_per_match:.3f}"
        )

        teams = conn.execute(
            """
            SELECT DISTINCT
                t.id,
                t.team_name
            FROM teams AS t
            INNER JOIN matches AS m
                ON (
                    t.id = m.home_team_id
                    OR t.id = m.away_team_id
                )
            WHERE m.league_id = ?
              AND m.season_id = ?
            ORDER BY t.team_name
            LIMIT 5
            """,
            (
                league_id,
                season_id,
            ),
        ).fetchall()

        for team_id, _team_name in teams:
            ratings = get_team_ratings(
                conn=conn,
                team_id=team_id,
                league_id=league_id,
                season_id=season_id,
            )

            print_team_ratings(ratings)

    finally:
        conn.close()


if __name__ == "__main__":
    main()