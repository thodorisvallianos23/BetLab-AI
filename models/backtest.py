import math
from dataclasses import dataclass

from database.connection import get_connection
from database.matches import get_matches
from models.dixon_coles import apply_dixon_coles
from models.expected_goals import get_expected_goals
from models.poisson_model import PoissonResult, run_poisson_model


MIN_PROBABILITY = 1e-15


@dataclass
class BacktestResult:
    matches_loaded: int
    matches_tested: int
    matches_skipped: int
    poisson_log_loss: float
    dixon_coles_log_loss: float
    poisson_brier_score: float
    dixon_coles_brier_score: float


def outcome_index(
    home_goals: int,
    away_goals: int,
) -> int:
    """
    0 = Home win
    1 = Draw
    2 = Away win
    """
    if home_goals > away_goals:
        return 0

    if home_goals < away_goals:
        return 2

    return 1


def get_1x2_probabilities(
    result: PoissonResult,
) -> tuple[float, float, float]:
    """
    Επιστρέφει τις πιθανότητες:
    Home win, Draw, Away win.
    """
    return (
        result.home_win_probability,
        result.draw_probability,
        result.away_win_probability,
    )


def calculate_log_loss(
    probabilities: tuple[float, float, float],
    actual_outcome: int,
) -> float:
    """
    Multiclass logarithmic loss για το πραγματικό αποτέλεσμα.
    Χαμηλότερη τιμή = καλύτερο μοντέλο.
    """
    actual_probability = probabilities[actual_outcome]

    safe_probability = max(
        MIN_PROBABILITY,
        min(1.0, actual_probability),
    )

    return -math.log(safe_probability)


def calculate_brier_score(
    probabilities: tuple[float, float, float],
    actual_outcome: int,
) -> float:
    """
    Multiclass Brier score.

    Υπολογίζει το άθροισμα των τετραγωνικών σφαλμάτων
    για Home, Draw και Away.

    Χαμηλότερη τιμή = καλύτερο μοντέλο.
    """
    score = 0.0

    for index, probability in enumerate(probabilities):
        actual_value = 1.0 if index == actual_outcome else 0.0
        score += (probability - actual_value) ** 2

    return score


def run_backtest() -> BacktestResult:
    """
    Εκτελεί season-aware historical backtest.

    Για κάθε αγώνα χρησιμοποιούνται μόνο δεδομένα
    πριν από την ημερομηνία του αγώνα, ώστε να
    αποφεύγεται το data leakage.
    """
    matches = get_matches(status="finished")

    poisson_log_loss_total = 0.0
    dixon_coles_log_loss_total = 0.0

    poisson_brier_total = 0.0
    dixon_coles_brier_total = 0.0

    matches_tested = 0
    matches_skipped = 0

    connection = get_connection()

    try:
        for match in matches:
            if (
                match.league_id is None
                or match.season_id is None
                or match.home_goals is None
                or match.away_goals is None
            ):
                matches_skipped += 1
                continue

            try:
                expected_goals = get_expected_goals(
                    conn=connection,
                    home_team_id=match.home_team_id,
                    away_team_id=match.away_team_id,
                    league_id=match.league_id,
                    season_id=match.season_id,
                    before_date=match.match_date,
                    recent_matches=5,
                    apply_form=True,
                )

                poisson_result = run_poisson_model(
                    home_expected_goals=(
                        expected_goals.home_expected_goals
                    ),
                    away_expected_goals=(
                        expected_goals.away_expected_goals
                    ),
                )

                dixon_coles_result = apply_dixon_coles(
                    poisson_result
                )

            except ValueError:
                # Συνήθως πρόκειται για αγώνα στην αρχή της
                # σεζόν χωρίς αρκετό προηγούμενο ιστορικό.
                matches_skipped += 1
                continue

            actual_outcome = outcome_index(
                home_goals=match.home_goals,
                away_goals=match.away_goals,
            )

            poisson_probabilities = get_1x2_probabilities(
                poisson_result
            )

            dixon_coles_probabilities = (
                get_1x2_probabilities(
                    dixon_coles_result.adjusted_result
                )
            )

            poisson_log_loss_total += calculate_log_loss(
                probabilities=poisson_probabilities,
                actual_outcome=actual_outcome,
            )

            dixon_coles_log_loss_total += calculate_log_loss(
                probabilities=dixon_coles_probabilities,
                actual_outcome=actual_outcome,
            )

            poisson_brier_total += calculate_brier_score(
                probabilities=poisson_probabilities,
                actual_outcome=actual_outcome,
            )

            dixon_coles_brier_total += calculate_brier_score(
                probabilities=dixon_coles_probabilities,
                actual_outcome=actual_outcome,
            )

            matches_tested += 1

    finally:
        connection.close()

    if matches_tested == 0:
        raise RuntimeError(
            "Backtest could not evaluate any matches."
        )

    return BacktestResult(
        matches_loaded=len(matches),
        matches_tested=matches_tested,
        matches_skipped=matches_skipped,
        poisson_log_loss=(
            poisson_log_loss_total / matches_tested
        ),
        dixon_coles_log_loss=(
            dixon_coles_log_loss_total / matches_tested
        ),
        poisson_brier_score=(
            poisson_brier_total / matches_tested
        ),
        dixon_coles_brier_score=(
            dixon_coles_brier_total / matches_tested
        ),
    )


def print_backtest_result(
    result: BacktestResult,
) -> None:
    print()
    print("BETLAB AI BACKTEST")
    print("=" * 60)

    print(f"Matches loaded:             {result.matches_loaded}")
    print(f"Matches tested:             {result.matches_tested}")
    print(f"Matches skipped:            {result.matches_skipped}")

    print()
    print("LOG LOSS")
    print("-" * 60)
    print(
        f"Pure Poisson:               "
        f"{result.poisson_log_loss:.6f}"
    )
    print(
        f"Dixon-Coles:                "
        f"{result.dixon_coles_log_loss:.6f}"
    )

    log_loss_difference = (
        result.poisson_log_loss
        - result.dixon_coles_log_loss
    )

    if log_loss_difference > 0:
        print(
            f"Winner:                     Dixon-Coles "
            f"({log_loss_difference:.6f} better)"
        )
    elif log_loss_difference < 0:
        print(
            f"Winner:                     Pure Poisson "
            f"({abs(log_loss_difference):.6f} better)"
        )
    else:
        print("Winner:                     Tie")

    print()
    print("BRIER SCORE")
    print("-" * 60)
    print(
        f"Pure Poisson:               "
        f"{result.poisson_brier_score:.6f}"
    )
    print(
        f"Dixon-Coles:                "
        f"{result.dixon_coles_brier_score:.6f}"
    )

    brier_difference = (
        result.poisson_brier_score
        - result.dixon_coles_brier_score
    )

    if brier_difference > 0:
        print(
            f"Winner:                     Dixon-Coles "
            f"({brier_difference:.6f} better)"
        )
    elif brier_difference < 0:
        print(
            f"Winner:                     Pure Poisson "
            f"({abs(brier_difference):.6f} better)"
        )
    else:
        print("Winner:                     Tie")


def main() -> None:
    result = run_backtest()
    print_backtest_result(result)


if __name__ == "__main__":
    main()
