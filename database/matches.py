import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "betlab_v2.db"


@dataclass(frozen=True)
class MatchRecord:
    id: int
    match_date: str
    league_id: Optional[int]
    season_id: Optional[int]
    season_name: Optional[str]
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    home_goals: Optional[int]
    away_goals: Optional[int]
    status: str


def _connect(
    db_path: Path = DEFAULT_DB_PATH,
) -> sqlite3.Connection:
    """
    Δημιουργεί σύνδεση με τη SQLite βάση.
    """
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database file not found: {db_path}"
        )

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    return connection


def _row_to_match(row: sqlite3.Row) -> MatchRecord:
    """
    Μετατρέπει μία SQLite row σε MatchRecord.
    """
    return MatchRecord(
        id=int(row["id"]),
        match_date=str(row["match_date"]),
        league_id=row["league_id"],
        season_id=row["season_id"],
        season_name=row["season_name"],
        home_team_id=int(row["home_team_id"]),
        home_team_name=str(row["home_team_name"]),
        away_team_id=int(row["away_team_id"]),
        away_team_name=str(row["away_team_name"]),
        home_goals=row["home_goals"],
        away_goals=row["away_goals"],
        status=str(row["status"]),
    )


def get_matches(
    season_id: Optional[int] = None,
    before_date: Optional[str] = None,
    status: Optional[str] = "finished",
    db_path: Path = DEFAULT_DB_PATH,
) -> list[MatchRecord]:
    """
    Επιστρέφει αγώνες με ονόματα ομάδων και σεζόν.

    Τα φίλτρα season_id, before_date και status
    είναι προαιρετικά.
    """
    query = """
        SELECT
            m.id,
            m.match_date,
            m.league_id,
            m.season_id,
            s.season_name,
            m.home_team_id,
            home.team_name AS home_team_name,
            m.away_team_id,
            away.team_name AS away_team_name,
            m.home_goals,
            m.away_goals,
            m.status
        FROM matches AS m
        JOIN teams AS home
            ON home.id = m.home_team_id
        JOIN teams AS away
            ON away.id = m.away_team_id
        LEFT JOIN seasons AS s
            ON s.id = m.season_id
        WHERE 1 = 1
    """

    parameters: list[object] = []

    if season_id is not None:
        query += " AND m.season_id = ?"
        parameters.append(season_id)

    if before_date is not None:
        query += " AND m.match_date < ?"
        parameters.append(before_date)

    if status is not None:
        query += " AND m.status = ?"
        parameters.append(status)

    query += " ORDER BY m.match_date, m.id"

    with _connect(db_path) as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [
        _row_to_match(row)
        for row in rows
    ]


def get_match_by_id(
    match_id: int,
    db_path: Path = DEFAULT_DB_PATH,
) -> Optional[MatchRecord]:
    """
    Επιστρέφει έναν αγώνα με βάση το ID του.
    """
    query = """
        SELECT
            m.id,
            m.match_date,
            m.league_id,
            m.season_id,
            s.season_name,
            m.home_team_id,
            home.team_name AS home_team_name,
            m.away_team_id,
            away.team_name AS away_team_name,
            m.home_goals,
            m.away_goals,
            m.status
        FROM matches AS m
        JOIN teams AS home
            ON home.id = m.home_team_id
        JOIN teams AS away
            ON away.id = m.away_team_id
        LEFT JOIN seasons AS s
            ON s.id = m.season_id
        WHERE m.id = ?
    """

    with _connect(db_path) as connection:
        row = connection.execute(
            query,
            (match_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_match(row)


def get_season_matches(
    season_id: int,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[MatchRecord]:
    """
    Επιστρέφει όλους τους ολοκληρωμένους αγώνες
    μιας συγκεκριμένης σεζόν.
    """
    return get_matches(
        season_id=season_id,
        status="finished",
        db_path=db_path,
    )


def get_matches_before_date(
    before_date: str,
    season_id: Optional[int] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[MatchRecord]:
    """
    Επιστρέφει ολοκληρωμένους αγώνες πριν από μία ημερομηνία.
    Χρησιμοποιείται για αποφυγή data leakage.
    """
    return get_matches(
        season_id=season_id,
        before_date=before_date,
        status="finished",
        db_path=db_path,
    )


def main() -> None:
    matches = get_matches()

    print()
    print("MATCH DATABASE")
    print("-" * 60)
    print(f"Matches loaded: {len(matches)}")

    if matches:
        first_match = matches[0]

        print(
            f"First match: "
            f"{first_match.home_team_name} "
            f"{first_match.home_goals}-"
            f"{first_match.away_goals} "
            f"{first_match.away_team_name}"
        )
        print(f"Date: {first_match.match_date}")
        print(f"Season: {first_match.season_name}")


if __name__ == "__main__":
    main()
