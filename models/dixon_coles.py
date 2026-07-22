import json
from dataclasses import dataclass
from pathlib import Path

from models.poisson_model import (
    PoissonResult,
    ScoreProbability,
    calculate_market_probabilities,
)

PARAMS_PATH = Path("data/dixon_coles_params.json")


@dataclass
class DixonColesParameters:
    rho: float


@dataclass
class DixonColesResult:
    rho: float
    poisson_result: PoissonResult
    adjusted_result: PoissonResult


def load_rho(
    params_path: Path = PARAMS_PATH,
) -> float:
    """
    Φορτώνει την εκπαιδευμένη παράμετρο rho
    από το JSON αρχείο.
    """
    if not params_path.exists():
        raise FileNotFoundError(
            f"Dixon-Coles parameters file not found: "
            f"{params_path}"
        )

    with params_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(file)

    if "rho" not in payload:
        raise ValueError(
            "The Dixon-Coles parameters file "
            "does not contain a 'rho' value."
        )

    rho = float(payload["rho"])

    if not -1.0 < rho < 1.0:
        raise ValueError(
            f"Invalid Dixon-Coles rho value: {rho}"
        )

    return rho
def dixon_coles_tau(
    home_goals: int,
    away_goals: int,
    home_expected_goals: float,
    away_expected_goals: float,
    rho: float,
) -> float:
    """
    Υπολογίζει τον Dixon-Coles correction factor
    για τα χαμηλά σκορ.
    """
    if home_goals == 0 and away_goals == 0:
        return 1.0 - (
            home_expected_goals
            * away_expected_goals
            * rho
        )

    if home_goals == 0 and away_goals == 1:
        return 1.0 + (
            home_expected_goals
            * rho
        )

    if home_goals == 1 and away_goals == 0:
        return 1.0 + (
            away_expected_goals
            * rho
        )

    if home_goals == 1 and away_goals == 1:
        return 1.0 - rho

    return 1.0


def adjust_score_matrix(
    poisson_result: PoissonResult,
    rho: float,
) -> list[ScoreProbability]:
    """
    Εφαρμόζει Dixon-Coles correction στον πίνακα σκορ
    και κανονικοποιεί τις πιθανότητες ώστε να αθροίζουν σε 1.
    """
    adjusted_scores: list[ScoreProbability] = []

    for score in poisson_result.score_probabilities:
        tau = dixon_coles_tau(
            home_goals=score.home_goals,
            away_goals=score.away_goals,
            home_expected_goals=(
                poisson_result.home_expected_goals
            ),
            away_expected_goals=(
                poisson_result.away_expected_goals
            ),
            rho=rho,
        )

        adjusted_probability = (
            score.probability
            * tau
        )

        if adjusted_probability < 0:
            raise ValueError(
                "Dixon-Coles produced a negative "
                f"probability for score "
                f"{score.home_goals}-{score.away_goals}."
            )

        adjusted_scores.append(
            ScoreProbability(
                home_goals=score.home_goals,
                away_goals=score.away_goals,
                probability=adjusted_probability,
            )
        )

    total_probability = sum(
        score.probability
        for score in adjusted_scores
    )

    if total_probability <= 0:
        raise ValueError(
            "Adjusted score matrix has zero probability."
        )

    return [
        ScoreProbability(
            home_goals=score.home_goals,
            away_goals=score.away_goals,
            probability=(
                score.probability
                / total_probability
            ),
        )
        for score in adjusted_scores
    ]
def apply_dixon_coles(
    poisson_result: PoissonResult,
) -> DixonColesResult:
    """
    Εφαρμόζει το Dixon-Coles adjustment
    και επιστρέφει νέο PoissonResult.
    """
    rho = load_rho()

    adjusted_scores = adjust_score_matrix(
        poisson_result=poisson_result,
        rho=rho,
    )

    adjusted_result = calculate_market_probabilities(
        score_probabilities=adjusted_scores,
        home_expected_goals=(
            poisson_result.home_expected_goals
        ),
        away_expected_goals=(
            poisson_result.away_expected_goals
        ),
        max_goals=poisson_result.max_goals,
    )

    return DixonColesResult(
        rho=rho,
        poisson_result=poisson_result,
        adjusted_result=adjusted_result,
    )
from models.poisson_model import (
    run_poisson_model,
    print_poisson_result,
)


def main() -> None:
    poisson = run_poisson_model(
        home_expected_goals=2.310,
        away_expected_goals=0.592,
    )

    result = apply_dixon_coles(poisson)

    print()
    print("PURE POISSON")
    print("=" * 55)
    print_poisson_result(result.poisson_result)

    print()
    print("DIXON-COLES ADJUSTED")
    print("=" * 55)
    print(f"Rho: {result.rho:.4f}")
    print_poisson_result(result.adjusted_result)


if __name__ == "__main__":
    main()