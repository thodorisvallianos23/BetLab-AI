import sqlite3
from database.connection import get_connection
from dataclasses import dataclass
from typing import Optional

from models.team_ratings import (
    DB_PATH,
    TeamRatings,
    get_league_averages,
    get_team_ratings,
)


@dataclass
class ExpectedGoalsResult:
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str

    league_id: int
    season_id: int
    before_date: Optional[str]

    home_expected_goals: float
    away_expected_goals: float

    home_attack_strength: float
    home_defence_strength: float
    away_attack_strength: float
    away_defence_strength: float

    home_form_multiplier: float
    away_form_multiplier: float


def form_multiplier(form_score: float) -> float:
    """
    Μετατρέπει τη βαθμολογία φόρμας 0-10
    σε έναν ελεγχόμενο πολλαπλασιαστή.

    0/10  -> 0.85
    5/10  -> 1.00
    10/10 -> 1.15
    """
    multiplier = 0.85 + (form_score / 10.0) * 0.30
    return max(0.85, min(multiplier, 1.15))


def validate_team_in_season(
    conn: sqlite3.Connection,
    team_id: int,
    league_id: int,
    season_id: int,
) -> None:
    """
    Ελέγχει ότι η ομάδα συμμετέχει
    στη συγκεκριμένη λίγκα και σεζόν.
    """
    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE league_id = ?
          AND season_id = ?
          AND (
              home_team_id = ?
              OR away_team_id = ?
          )
        """,
        (
            league_id,
            season_id,
            team_id,
            team_id,
        ),
    ).fetchone()

    if not row or row[0] == 0:
        raise ValueError(
            f"Team ID {team_id} has no matches "
            f"in league {league_id}, season {season_id}."
        )


def get_expected_goals(
    conn: sqlite3.Connection,
    home_team_id: int,
    away_team_id: int,
    league_id: int,
    season_id: int,
    before_date: Optional[str] = None,
    recent_matches: int = 5,
    apply_form: bool = True,
) -> ExpectedGoalsResult:
    """
    Υπολογίζει τα expected goals ενός αγώνα.

    Χρησιμοποιεί αποκλειστικά δεδομένα:
    - της επιλεγμένης λίγκας,
    - της επιλεγμένης σεζόν,
    - πριν από το before_date, όταν έχει δοθεί.

    Έτσι αποφεύγεται το data leakage.
    """
    if home_team_id == away_team_id:
        raise ValueError(
            "Home team and away team cannot be the same."
        )

    validate_team_in_season(
        conn=conn,
        team_id=home_team_id,
        league_id=league_id,
        season_id=season_id,
    )

    validate_team_in_season(
        conn=conn,
        team_id=away_team_id,
        league_id=league_id,
        season_id=season_id,
    )

    league = get_league_averages(
        conn=conn,
        league_id=league_id,
        season_id=season_id,
        before_date=before_date,
    )

    if league.matches == 0:
        raise ValueError(
            "No finished matches are available "
            "for the selected league, season and date."
        )

    home_ratings: TeamRatings = get_team_ratings(
        conn=conn,
        team_id=home_team_id,
        league_id=league_id,
        season_id=season_id,
        before_date=before_date,
        recent_matches=recent_matches,
    )

    away_ratings: TeamRatings = get_team_ratings(
        conn=conn,
        team_id=away_team_id,
        league_id=league_id,
        season_id=season_id,
        before_date=before_date,
        recent_matches=recent_matches,
    )

    home_base_xg = (
        league.home_goals_per_match
        * home_ratings.home_attack_strength
        * away_ratings.away_defence_strength
    )

    away_base_xg = (
        league.away_goals_per_match
        * away_ratings.away_attack_strength
        * home_ratings.home_defence_strength
    )

    if apply_form:
        home_form = form_multiplier(
            home_ratings.recent_form_score
        )

        away_form = form_multiplier(
            away_ratings.recent_form_score
        )
    else:
        home_form = 1.0
        away_form = 1.0

    home_expected_goals = home_base_xg * home_form
    away_expected_goals = away_base_xg * away_form

    # Προστασία από ακραίες ή μη ρεαλιστικές τιμές.
    home_expected_goals = max(
        0.20,
        min(home_expected_goals, 4.50),
    )

    away_expected_goals = max(
        0.20,
        min(away_expected_goals, 4.50),
    )

    return ExpectedGoalsResult(
        home_team_id=home_team_id,
        home_team_name=home_ratings.team_name,
        away_team_id=away_team_id,
        away_team_name=away_ratings.team_name,
        league_id=league_id,
        season_id=season_id,
        before_date=before_date,
        home_expected_goals=home_expected_goals,
        away_expected_goals=away_expected_goals,
        home_attack_strength=home_ratings.home_attack_strength,
        home_defence_strength=home_ratings.home_defence_strength,
        away_attack_strength=away_ratings.away_attack_strength,
        away_defence_strength=away_ratings.away_defence_strength,
        home_form_multiplier=home_form,
        away_form_multiplier=away_form,
    )


def print_expected_goals(
    result: ExpectedGoalsResult,
) -> None:
    print()
    print(
        f"{result.home_team_name} "
        f"vs {result.away_team_name}"
    )
    print("-" * 55)

    print(f"League ID:                 {result.league_id}")
    print(f"Season ID:                 {result.season_id}")
    print(f"Before date:               {result.before_date}")

    print()
    print(
        f"{result.home_team_name} home attack:      "
        f"{result.home_attack_strength:.3f}"
    )
    print(
        f"{result.away_team_name} away defence:     "
        f"{result.away_defence_strength:.3f}"
    )
    print(
        f"{result.away_team_name} away attack:      "
        f"{result.away_attack_strength:.3f}"
    )
    print(
        f"{result.home_team_name} home defence:     "
        f"{result.home_defence_strength:.3f}"
    )

    print()
    print(
        f"{result.home_team_name} form multiplier:  "
        f"{result.home_form_multiplier:.3f}"
    )
    print(
        f"{result.away_team_name} form multiplier:  "
        f"{result.away_form_multiplier:.3f}"
    )

    print()
    print(
        f"Expected home goals:       "
        f"{result.home_expected_goals:.3f}"
    )
    print(
        f"Expected away goals:       "
        f"{result.away_expected_goals:.3f}"
    )
    print(
        f"Expected total goals:      "
        f"{result.home_expected_goals + result.away_expected_goals:.3f}"
    )


def main() -> None:
    conn = get_connection()

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
                "No league found in the database."
            )

        if not season_row:
            raise ValueError(
                "No season found in the database."
            )

        league_id = league_row[0]
        season_id = season_row[0]
        season_name = season_row[1]

        teams = conn.execute(
            """
            SELECT
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
            GROUP BY
                t.id,
                t.team_name
            ORDER BY
                t.team_name
            """,
            (
                league_id,
                season_id,
            ),
        ).fetchall()

        if len(teams) < 2:
            raise ValueError(
                "Not enough teams are available "
                "for the selected season."
            )

        print()
        print(f"SEASON: {season_name}")
        print("AVAILABLE TEAMS")
        print("-" * 55)

        for team_id, team_name in teams:
            print(f"{team_id}: {team_name}")

        home_team_id = teams[0][0]
        away_team_id = teams[1][0]

        result = get_expected_goals(
            conn=conn,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            league_id=league_id,
            season_id=season_id,
            before_date=None,
            recent_matches=5,
            apply_form=True,
        )

        print_expected_goals(result)

    finally:
        conn.close()


if __name__ == "__main__":
    main()