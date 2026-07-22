import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from expected_goals import get_expected_goals
from team_ratings import DB_PATH


OUTPUT_PATH = Path("data/dixon_coles_params.json")


@dataclass
class HistoricalPrediction:
    match_id: int
    match_date: str

    home_team_id: int
    away_team_id: int

    actual_home_goals: int
    actual_away_goals: int

    home_expected_goals: float
    away_expected_goals: float


@dataclass
class DixonColesFitResult:
    league_id: int
    season_id: int
    rho: float
    log_likelihood: float
    matches_used: int
    matches_skipped: int


def poisson_probability(
    expected_goals: float,
    goals: int,
) -> float:
    """
    Πιθανότητα να σημειωθούν ακριβώς k γκολ
    σύμφωνα με κατανομή Poisson.
    """
    if expected_goals <= 0:
        raise ValueError(
            "Expected goals must be greater than zero."
        )

    if goals < 0:
        raise ValueError(
            "Goals cannot be negative."
        )

    return (
        math.exp(-expected_goals)
        * expected_goals**goals
        / math.factorial(goals)
    )


def dixon_coles_tau(
    home_goals: int,
    away_goals: int,
    home_expected_goals: float,
    away_expected_goals: float,
    rho: float,
) -> float:
    """
    Dixon-Coles correction για τα χαμηλά σκορ:

    0-0
    0-1
    1-0
    1-1
    """
    home_xg = home_expected_goals
    away_xg = away_expected_goals

    if home_goals == 0 and away_goals == 0:
        tau = 1.0 - (
            home_xg
            * away_xg
            * rho
        )

    elif home_goals == 0 and away_goals == 1:
        tau = 1.0 + (
            home_xg
            * rho
        )

    elif home_goals == 1 and away_goals == 0:
        tau = 1.0 + (
            away_xg
            * rho
        )

    elif home_goals == 1 and away_goals == 1:
        tau = 1.0 - rho

    else:
        tau = 1.0

    return tau


def count_finished_matches_before_date(
    conn: sqlite3.Connection,
    league_id: int,
    season_id: int,
    before_date: str,
) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE league_id = ?
          AND season_id = ?
          AND LOWER(status) = 'finished'
          AND home_goals IS NOT NULL
          AND away_goals IS NOT NULL
          AND match_date < ?
        """,
        (
            league_id,
            season_id,
            before_date,
        ),
    ).fetchone()

    return int(row[0] or 0)


def build_historical_predictions(
    conn: sqlite3.Connection,
    league_id: int,
    season_id: int,
    recent_matches: int = 5,
    minimum_previous_matches: int = 30,
) -> tuple[list[HistoricalPrediction], int]:
    """
    Δημιουργεί ιστορικές προβλέψεις χρησιμοποιώντας
    μόνο δεδομένα πριν από κάθε αγώνα.

    Οι πρώτοι αγώνες της σεζόν παραλείπονται επειδή
    δεν υπάρχει αρκετό δείγμα για σταθερά ratings.
    """
    rows = conn.execute(
        """
        SELECT
            id,
            match_date,
            home_team_id,
            away_team_id,
            home_goals,
            away_goals
        FROM matches
        WHERE league_id = ?
          AND season_id = ?
          AND LOWER(status) = 'finished'
          AND home_goals IS NOT NULL
          AND away_goals IS NOT NULL
        ORDER BY
            match_date ASC,
            id ASC
        """,
        (
            league_id,
            season_id,
        ),
    ).fetchall()

    predictions: list[HistoricalPrediction] = []
    skipped = 0

    for (
        match_id,
        match_date,
        home_team_id,
        away_team_id,
        home_goals,
        away_goals,
    ) in rows:
        previous_matches = (
            count_finished_matches_before_date(
                conn=conn,
                league_id=league_id,
                season_id=season_id,
                before_date=match_date,
            )
        )

        if previous_matches < minimum_previous_matches:
            skipped += 1
            continue

        try:
            expected = get_expected_goals(
                conn=conn,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                league_id=league_id,
                season_id=season_id,
                before_date=match_date,
                recent_matches=recent_matches,
                apply_form=True,
            )

        except ValueError as error:
            print(
                f"Skipping match {match_id}: {error}"
            )
            skipped += 1
            continue

        predictions.append(
            HistoricalPrediction(
                match_id=match_id,
                match_date=match_date,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                actual_home_goals=int(home_goals),
                actual_away_goals=int(away_goals),
                home_expected_goals=(
                    expected.home_expected_goals
                ),
                away_expected_goals=(
                    expected.away_expected_goals
                ),
            )
        )

    return predictions, skipped


def calculate_log_likelihood(
    predictions: list[HistoricalPrediction],
    rho: float,
) -> Optional[float]:
    """
    Υπολογίζει το συνολικό log-likelihood
    για μία υποψήφια τιμή rho.
    """
    total_log_likelihood = 0.0

    for prediction in predictions:
        tau = dixon_coles_tau(
            home_goals=prediction.actual_home_goals,
            away_goals=prediction.actual_away_goals,
            home_expected_goals=(
                prediction.home_expected_goals
            ),
            away_expected_goals=(
                prediction.away_expected_goals
            ),
            rho=rho,
        )

        # Μη έγκυρη τιμή rho για αυτά τα xG.
        if tau <= 0:
            return None

        home_probability = poisson_probability(
            prediction.home_expected_goals,
            prediction.actual_home_goals,
        )

        away_probability = poisson_probability(
            prediction.away_expected_goals,
            prediction.actual_away_goals,
        )

        adjusted_probability = (
            home_probability
            * away_probability
            * tau
        )

        if adjusted_probability <= 0:
            return None

        total_log_likelihood += math.log(
            adjusted_probability
        )

    return total_log_likelihood


def fit_rho(
    predictions: list[HistoricalPrediction],
    rho_min: float = -0.20,
    rho_max: float = 0.20,
    step: float = 0.001,
) -> tuple[float, float]:
    """
    Grid search για την τιμή rho που μεγιστοποιεί
    το log-likelihood των πραγματικών αποτελεσμάτων.
    """
    if not predictions:
        raise ValueError(
            "No historical predictions available."
        )

    best_rho: Optional[float] = None
    best_log_likelihood = float("-inf")

    number_of_steps = round(
        (rho_max - rho_min) / step
    )

    for index in range(number_of_steps + 1):
        rho = rho_min + index * step
        rho = round(rho, 6)

        log_likelihood = calculate_log_likelihood(
            predictions=predictions,
            rho=rho,
        )

        if log_likelihood is None:
            continue

        if log_likelihood > best_log_likelihood:
            best_rho = rho
            best_log_likelihood = log_likelihood

    if best_rho is None:
        raise ValueError(
            "Could not find a valid rho value."
        )

    return best_rho, best_log_likelihood


def save_fit_result(
    result: DixonColesFitResult,
    output_path: Path = OUTPUT_PATH,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "league_id": result.league_id,
        "season_id": result.season_id,
        "rho": result.rho,
        "log_likelihood": result.log_likelihood,
        "matches_used": result.matches_used,
        "matches_skipped": result.matches_skipped,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=4,
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
                "No league found."
            )

        if not season_row:
            raise ValueError(
                "No season found."
            )

        league_id = int(league_row[0])
        season_id = int(season_row[0])
        season_name = season_row[1]

        print()
        print("DIXON-COLES TRAINING")
        print("-" * 55)
        print(f"Season:                    {season_name}")
        print(f"League ID:                 {league_id}")
        print(f"Season ID:                 {season_id}")
        print()
        print("Building historical predictions...")

        predictions, skipped = (
            build_historical_predictions(
                conn=conn,
                league_id=league_id,
                season_id=season_id,
                recent_matches=5,
                minimum_previous_matches=30,
            )
        )

        print(
            f"Historical predictions:    "
            f"{len(predictions)}"
        )
        print(
            f"Matches skipped:           "
            f"{skipped}"
        )

        print()
        print("Searching for optimal rho...")

        rho, log_likelihood = fit_rho(
            predictions=predictions,
            rho_min=-0.20,
            rho_max=0.20,
            step=0.001,
        )

        result = DixonColesFitResult(
            league_id=league_id,
            season_id=season_id,
            rho=rho,
            log_likelihood=log_likelihood,
            matches_used=len(predictions),
            matches_skipped=skipped,
        )

        save_fit_result(result)

        print()
        print("TRAINING RESULT")
        print("-" * 55)
        print(f"Optimal rho:               {rho:.4f}")
        print(
            f"Log-likelihood:            "
            f"{log_likelihood:.3f}"
        )
        print(
            f"Matches used:              "
            f"{len(predictions)}"
        )
        print(
            f"Saved to:                  "
            f"{OUTPUT_PATH}"
        )

    finally:
        conn.close()


if __name__ == "__main__":
    main()