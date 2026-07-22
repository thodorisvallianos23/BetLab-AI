from dataclasses import dataclass
from typing import Any, Optional

from database.connection import get_connection
from models.dixon_coles import apply_dixon_coles
from models.expected_goals import get_expected_goals
from models.poisson_model import PoissonResult, run_poisson_model


@dataclass(frozen=True)
class ScorePrediction:
    home_goals: int
    away_goals: int
    probability: float
    fair_odds: float


@dataclass(frozen=True)
class PredictionResult:
    home_team_id: int
    away_team_id: int
    league_id: int
    season_id: int

    home_expected_goals: float
    away_expected_goals: float
    total_expected_goals: float

    home_win_probability: float
    draw_probability: float
    away_win_probability: float

    over_15_probability: float
    under_15_probability: float
    over_25_probability: float
    under_25_probability: float
    over_35_probability: float
    under_35_probability: float

    btts_yes_probability: float
    btts_no_probability: float

    fair_home_odds: float
    fair_draw_odds: float
    fair_away_odds: float

    fair_over_15_odds: float
    fair_under_15_odds: float
    fair_over_25_odds: float
    fair_under_25_odds: float
    fair_over_35_odds: float
    fair_under_35_odds: float

    fair_btts_yes_odds: float
    fair_btts_no_odds: float

    most_likely_score: ScorePrediction
    top_scores: list[ScorePrediction]

    model_name: str


def fair_odds(probability: float) -> float:
    if probability <= 0.0:
        return 0.0
    return 1.0 / probability


def clamp_probability(probability: float) -> float:
    return max(0.0, min(1.0, float(probability)))


def get_market_probability(
    probabilities: dict[float, float],
    line: float,
) -> float:
    if line in probabilities:
        return clamp_probability(probabilities[line])

    string_line = str(line)
    if string_line in probabilities:
        return clamp_probability(probabilities[string_line])  # type: ignore[index]

    raise KeyError(
        f"Missing goals line {line} in probabilities: "
        f"{list(probabilities.keys())}"
    )


def unpack_score_probability(score: Any) -> tuple[int, int, float]:
    if hasattr(score, "home_goals"):
        return (
            int(score.home_goals),
            int(score.away_goals),
            float(score.probability),
        )

    if isinstance(score, dict):
        return (
            int(score["home_goals"]),
            int(score["away_goals"]),
            float(score["probability"]),
        )

    if isinstance(score, (tuple, list)) and len(score) >= 3:
        return int(score[0]), int(score[1]), float(score[2])

    raise TypeError(
        "Unsupported score probability item: "
        f"{type(score).__name__}"
    )


def get_top_score_predictions(
    result: PoissonResult,
    limit: int = 5,
) -> list[ScorePrediction]:
    if limit <= 0:
        raise ValueError("top_score_limit must be greater than zero.")

    scores: list[ScorePrediction] = []

    for score in result.score_probabilities:
        home_goals, away_goals, probability = unpack_score_probability(score)
        probability = clamp_probability(probability)

        scores.append(
            ScorePrediction(
                home_goals=home_goals,
                away_goals=away_goals,
                probability=probability,
                fair_odds=fair_odds(probability),
            )
        )

    if not scores:
        raise ValueError("PoissonResult.score_probabilities is empty.")

    scores.sort(key=lambda item: item.probability, reverse=True)
    return scores[:limit]


def build_prediction_result(
    home_team_id: int,
    away_team_id: int,
    league_id: int,
    season_id: int,
    home_expected_goals: float,
    away_expected_goals: float,
    model_result: PoissonResult,
    model_name: str,
    top_score_limit: int,
) -> PredictionResult:
    over_15 = get_market_probability(model_result.over_probabilities, 1.5)
    under_15 = get_market_probability(model_result.under_probabilities, 1.5)
    over_25 = get_market_probability(model_result.over_probabilities, 2.5)
    under_25 = get_market_probability(model_result.under_probabilities, 2.5)
    over_35 = get_market_probability(model_result.over_probabilities, 3.5)
    under_35 = get_market_probability(model_result.under_probabilities, 3.5)

    btts_yes = clamp_probability(model_result.btts_yes_probability)
    btts_no = clamp_probability(model_result.btts_no_probability)

    top_scores = get_top_score_predictions(
        result=model_result,
        limit=top_score_limit,
    )

    return PredictionResult(
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        league_id=league_id,
        season_id=season_id,
        home_expected_goals=home_expected_goals,
        away_expected_goals=away_expected_goals,
        total_expected_goals=home_expected_goals + away_expected_goals,
        home_win_probability=clamp_probability(model_result.home_win_probability),
        draw_probability=clamp_probability(model_result.draw_probability),
        away_win_probability=clamp_probability(model_result.away_win_probability),
        over_15_probability=over_15,
        under_15_probability=under_15,
        over_25_probability=over_25,
        under_25_probability=under_25,
        over_35_probability=over_35,
        under_35_probability=under_35,
        btts_yes_probability=btts_yes,
        btts_no_probability=btts_no,
        fair_home_odds=fair_odds(model_result.home_win_probability),
        fair_draw_odds=fair_odds(model_result.draw_probability),
        fair_away_odds=fair_odds(model_result.away_win_probability),
        fair_over_15_odds=fair_odds(over_15),
        fair_under_15_odds=fair_odds(under_15),
        fair_over_25_odds=fair_odds(over_25),
        fair_under_25_odds=fair_odds(under_25),
        fair_over_35_odds=fair_odds(over_35),
        fair_under_35_odds=fair_odds(under_35),
        fair_btts_yes_odds=fair_odds(btts_yes),
        fair_btts_no_odds=fair_odds(btts_no),
        most_likely_score=top_scores[0],
        top_scores=top_scores,
        model_name=model_name,
    )


def predict_match(
    home_team_id: int,
    away_team_id: int,
    league_id: int,
    season_id: int,
    before_date: Optional[str] = None,
    recent_matches: int = 5,
    apply_form: bool = True,
    use_dixon_coles: bool = False,
    max_goals: int = 10,
    top_score_limit: int = 5,
) -> PredictionResult:
    if home_team_id == away_team_id:
        raise ValueError("Home and away teams must be different.")

    connection = get_connection()

    try:
        expected_goals = get_expected_goals(
            conn=connection,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            league_id=league_id,
            season_id=season_id,
            before_date=before_date,
            recent_matches=recent_matches,
            apply_form=apply_form,
        )
    finally:
        connection.close()

    poisson_result = run_poisson_model(
        home_expected_goals=expected_goals.home_expected_goals,
        away_expected_goals=expected_goals.away_expected_goals,
        max_goals=max_goals,
    )

    if use_dixon_coles:
        adjusted = apply_dixon_coles(poisson_result)
        model_result = adjusted.adjusted_result
        model_name = "Dixon-Coles"
    else:
        model_result = poisson_result
        model_name = "Pure Poisson"

    return build_prediction_result(
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        league_id=league_id,
        season_id=season_id,
        home_expected_goals=expected_goals.home_expected_goals,
        away_expected_goals=expected_goals.away_expected_goals,
        model_result=model_result,
        model_name=model_name,
        top_score_limit=top_score_limit,
    )


def print_prediction(result: PredictionResult) -> None:
    print()
    print("BETLAB AI MATCH PREDICTION")
    print("=" * 60)
    print(f"Model:                  {result.model_name}")

    print()
    print("EXPECTED GOALS")
    print("-" * 60)
    print(f"Home xG:                {result.home_expected_goals:.3f}")
    print(f"Away xG:                {result.away_expected_goals:.3f}")
    print(f"Total xG:               {result.total_expected_goals:.3f}")

    print()
    print("1X2 PROBABILITIES")
    print("-" * 60)
    print(
        f"Home win:               {result.home_win_probability:.2%} "
        f"(fair odds {result.fair_home_odds:.2f})"
    )
    print(
        f"Draw:                   {result.draw_probability:.2%} "
        f"(fair odds {result.fair_draw_odds:.2f})"
    )
    print(
        f"Away win:               {result.away_win_probability:.2%} "
        f"(fair odds {result.fair_away_odds:.2f})"
    )

    print()
    print("GOALS MARKETS")
    print("-" * 60)
    print(
        f"Over 1.5:               {result.over_15_probability:.2%} "
        f"(fair odds {result.fair_over_15_odds:.2f})"
    )
    print(
        f"Over 2.5:               {result.over_25_probability:.2%} "
        f"(fair odds {result.fair_over_25_odds:.2f})"
    )
    print(
        f"Over 3.5:               {result.over_35_probability:.2%} "
        f"(fair odds {result.fair_over_35_odds:.2f})"
    )
    print(
        f"BTTS Yes:               {result.btts_yes_probability:.2%} "
        f"(fair odds {result.fair_btts_yes_odds:.2f})"
    )

    print()
    print("MOST LIKELY SCORE")
    print("-" * 60)
    score = result.most_likely_score
    print(
        f"{score.home_goals}-{score.away_goals} "
        f"({score.probability:.2%}, fair odds {score.fair_odds:.2f})"
    )

    print()
    print("TOP SCORES")
    print("-" * 60)

    for index, score in enumerate(result.top_scores, start=1):
        print(
            f"{index}. {score.home_goals}-{score.away_goals}: "
            f"{score.probability:.2%} "
            f"(fair odds {score.fair_odds:.2f})"
        )


def main() -> None:
    result = predict_match(
        home_team_id=18,
        away_team_id=3,
        league_id=1,
        season_id=1,
        use_dixon_coles=True,
    )

    print_prediction(result)


if __name__ == "__main__":
    main()