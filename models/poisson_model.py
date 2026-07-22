import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ScoreProbability:
    home_goals: int
    away_goals: int
    probability: float


@dataclass
class PoissonResult:
    home_expected_goals: float
    away_expected_goals: float
    max_goals: int

    home_win_probability: float
    draw_probability: float
    away_win_probability: float

    over_probabilities: Dict[float, float]
    under_probabilities: Dict[float, float]

    btts_yes_probability: float
    btts_no_probability: float

    most_likely_score: Tuple[int, int]
    most_likely_score_probability: float

    score_probabilities: List[ScoreProbability]
    probability_coverage: float


def poisson_probability(
    expected_goals: float,
    goals: int,
) -> float:
    """
    Υπολογίζει την πιθανότητα μια ομάδα να σκοράρει
    ακριβώς συγκεκριμένο αριθμό γκολ.

    P(X = k) = e^(-λ) * λ^k / k!
    """
    if expected_goals < 0:
        raise ValueError(
            "Expected goals cannot be negative."
        )

    if goals < 0:
        raise ValueError(
            "Goals cannot be negative."
        )

    return (
        math.exp(-expected_goals)
        * (expected_goals ** goals)
        / math.factorial(goals)
    )


def build_score_matrix(
    home_expected_goals: float,
    away_expected_goals: float,
    max_goals: int = 10,
) -> List[ScoreProbability]:
    """
    Δημιουργεί όλες τις πιθανότητες σκορ από 0-0
    μέχρι max_goals-max_goals.
    """
    if max_goals < 1:
        raise ValueError(
            "max_goals must be at least 1."
        )

    home_probabilities = [
        poisson_probability(
            home_expected_goals,
            goals,
        )
        for goals in range(max_goals + 1)
    ]

    away_probabilities = [
        poisson_probability(
            away_expected_goals,
            goals,
        )
        for goals in range(max_goals + 1)
    ]

    score_probabilities: List[ScoreProbability] = []

    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            probability = (
                home_probabilities[home_goals]
                * away_probabilities[away_goals]
            )

            score_probabilities.append(
                ScoreProbability(
                    home_goals=home_goals,
                    away_goals=away_goals,
                    probability=probability,
                )
            )

    return score_probabilities


def calculate_market_probabilities(
    score_probabilities: List[ScoreProbability],
    home_expected_goals: float,
    away_expected_goals: float,
    max_goals: int = 10,
) -> PoissonResult:
    """
    Μετατρέπει τον πίνακα σκορ σε αγορές:

    - 1X2
    - Over / Under
    - BTTS
    - Correct Score
    """
    if not score_probabilities:
        raise ValueError(
            "Score probability matrix is empty."
        )

    home_win_probability = 0.0
    draw_probability = 0.0
    away_win_probability = 0.0

    over_lines = [
        0.5,
        1.5,
        2.5,
        3.5,
        4.5,
    ]

    over_probabilities = {
        line: 0.0
        for line in over_lines
    }

    btts_yes_probability = 0.0
    probability_coverage = 0.0

    most_likely = max(
        score_probabilities,
        key=lambda item: item.probability,
    )

    for score in score_probabilities:
        probability = score.probability
        total_goals = (
            score.home_goals
            + score.away_goals
        )

        probability_coverage += probability

        if score.home_goals > score.away_goals:
            home_win_probability += probability

        elif score.home_goals == score.away_goals:
            draw_probability += probability

        else:
            away_win_probability += probability

        for line in over_lines:
            if total_goals > line:
                over_probabilities[line] += probability

        if (
            score.home_goals > 0
            and score.away_goals > 0
        ):
            btts_yes_probability += probability

    under_probabilities = {
        line: max(
            0.0,
            probability_coverage
            - over_probabilities[line],
        )
        for line in over_lines
    }

    btts_no_probability = max(
        0.0,
        probability_coverage
        - btts_yes_probability,
    )

    return PoissonResult(
        home_expected_goals=home_expected_goals,
        away_expected_goals=away_expected_goals,
        max_goals=max_goals,
        home_win_probability=home_win_probability,
        draw_probability=draw_probability,
        away_win_probability=away_win_probability,
        over_probabilities=over_probabilities,
        under_probabilities=under_probabilities,
        btts_yes_probability=btts_yes_probability,
        btts_no_probability=btts_no_probability,
        most_likely_score=(
            most_likely.home_goals,
            most_likely.away_goals,
        ),
        most_likely_score_probability=(
            most_likely.probability
        ),
        score_probabilities=score_probabilities,
        probability_coverage=probability_coverage,
    )


def run_poisson_model(
    home_expected_goals: float,
    away_expected_goals: float,
    max_goals: int = 10,
) -> PoissonResult:
    """
    Κεντρική συνάρτηση του Poisson model.
    """
    score_matrix = build_score_matrix(
        home_expected_goals=home_expected_goals,
        away_expected_goals=away_expected_goals,
        max_goals=max_goals,
    )

    return calculate_market_probabilities(
        score_probabilities=score_matrix,
        home_expected_goals=home_expected_goals,
        away_expected_goals=away_expected_goals,
        max_goals=max_goals,
    )


def get_top_correct_scores(
    result: PoissonResult,
    limit: int = 10,
) -> List[ScoreProbability]:
    """
    Επιστρέφει τα πιθανότερα correct scores.
    """
    if limit <= 0:
        return []

    return sorted(
        result.score_probabilities,
        key=lambda item: item.probability,
        reverse=True,
    )[:limit]


def probability_to_percentage(
    probability: float,
) -> float:
    return probability * 100.0


def print_poisson_result(
    result: PoissonResult,
    top_scores: int = 10,
) -> None:
    print()
    print("POISSON MODEL")
    print("-" * 55)

    print(
        f"Home expected goals:       "
        f"{result.home_expected_goals:.3f}"
    )
    print(
        f"Away expected goals:       "
        f"{result.away_expected_goals:.3f}"
    )
    print(
        f"Probability coverage:      "
        f"{probability_to_percentage(result.probability_coverage):.6f}%"
    )

    print()
    print("1X2")
    print("-" * 55)
    print(
        f"Home win:                  "
        f"{probability_to_percentage(result.home_win_probability):.2f}%"
    )
    print(
        f"Draw:                      "
        f"{probability_to_percentage(result.draw_probability):.2f}%"
    )
    print(
        f"Away win:                  "
        f"{probability_to_percentage(result.away_win_probability):.2f}%"
    )

    print()
    print("OVER / UNDER")
    print("-" * 55)

    for line in sorted(result.over_probabilities):
        over_probability = (
            result.over_probabilities[line]
        )
        under_probability = (
            result.under_probabilities[line]
        )

        print(
            f"Over {line:<3}:                 "
            f"{probability_to_percentage(over_probability):.2f}%"
        )
        print(
            f"Under {line:<3}:                "
            f"{probability_to_percentage(under_probability):.2f}%"
        )

    print()
    print("BTTS")
    print("-" * 55)
    print(
        f"BTTS Yes:                  "
        f"{probability_to_percentage(result.btts_yes_probability):.2f}%"
    )
    print(
        f"BTTS No:                   "
        f"{probability_to_percentage(result.btts_no_probability):.2f}%"
    )

    print()
    print("MOST LIKELY SCORE")
    print("-" * 55)
    print(
        f"{result.most_likely_score[0]}-"
        f"{result.most_likely_score[1]}: "
        f"{probability_to_percentage(result.most_likely_score_probability):.2f}%"
    )

    print()
    print(f"TOP {top_scores} CORRECT SCORES")
    print("-" * 55)

    for score in get_top_correct_scores(
        result,
        limit=top_scores,
    ):
        print(
            f"{score.home_goals}-"
            f"{score.away_goals}: "
            f"{probability_to_percentage(score.probability):.2f}%"
        )


def main() -> None:
    home_expected_goals = 2.310
    away_expected_goals = 0.592

    result = run_poisson_model(
        home_expected_goals=home_expected_goals,
        away_expected_goals=away_expected_goals,
        max_goals=10,
    )

    print_poisson_result(
        result=result,
        top_scores=10,
    )


if __name__ == "__main__":
    main()