from dataclasses import dataclass
from typing import Dict, List

from models.bankroll import calculate_stake
from models.prediction_engine import PredictionResult


@dataclass(frozen=True)
class ValueBetResult:
    probability: float
    fair_odds: float
    bookmaker_odds: float

    edge: float
    expected_value: float

    kelly_fraction: float
    half_kelly: float
    quarter_kelly: float

    is_value: bool


@dataclass(frozen=True)
class MarketValueBet:
    market: str
    result: ValueBetResult


def fair_odds(probability: float) -> float:
    if probability <= 0.0:
        return 0.0

    return 1.0 / probability


def calculate_edge(
    fair_odds_value: float,
    bookmaker_odds: float,
) -> float:
    if fair_odds_value <= 0.0:
        return 0.0

    return (
        bookmaker_odds / fair_odds_value
    ) - 1.0


def calculate_expected_value(
    probability: float,
    bookmaker_odds: float,
) -> float:
    return (
        probability * bookmaker_odds
    ) - 1.0


def calculate_kelly_fraction(
    probability: float,
    bookmaker_odds: float,
) -> float:
    if bookmaker_odds <= 1.0:
        return 0.0

    decimal_profit = bookmaker_odds - 1.0
    loss_probability = 1.0 - probability

    kelly = (
        decimal_profit * probability
        - loss_probability
    ) / decimal_profit

    return max(0.0, kelly)


def evaluate_value_bet(
    probability: float,
    bookmaker_odds: float,
    minimum_edge: float = 0.02,
) -> ValueBetResult:
    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "Probability must be between 0 and 1."
        )

    if bookmaker_odds <= 1.0:
        raise ValueError(
            "Bookmaker odds must be greater than 1.0."
        )

    fair = fair_odds(probability)

    edge = calculate_edge(
        fair_odds_value=fair,
        bookmaker_odds=bookmaker_odds,
    )

    expected_value = calculate_expected_value(
        probability=probability,
        bookmaker_odds=bookmaker_odds,
    )

    kelly = calculate_kelly_fraction(
        probability=probability,
        bookmaker_odds=bookmaker_odds,
    )

    return ValueBetResult(
        probability=probability,
        fair_odds=fair,
        bookmaker_odds=bookmaker_odds,
        edge=edge,
        expected_value=expected_value,
        kelly_fraction=kelly,
        half_kelly=kelly / 2.0,
        quarter_kelly=kelly / 4.0,
        is_value=(
            edge >= minimum_edge
            and expected_value > 0.0
        ),
    )


def evaluate_prediction_markets(
    prediction: PredictionResult,
    bookmaker_odds: Dict[str, float],
    minimum_edge: float = 0.02,
) -> List[MarketValueBet]:
    market_probabilities = {
        "home_win": prediction.home_win_probability,
        "draw": prediction.draw_probability,
        "away_win": prediction.away_win_probability,

        "over_15": prediction.over_15_probability,
        "under_15": prediction.under_15_probability,

        "over_25": prediction.over_25_probability,
        "under_25": prediction.under_25_probability,

        "over_35": prediction.over_35_probability,
        "under_35": prediction.under_35_probability,

        "btts_yes": prediction.btts_yes_probability,
        "btts_no": prediction.btts_no_probability,
    }

    results: List[MarketValueBet] = []

    for market, probability in market_probabilities.items():
        if market not in bookmaker_odds:
            continue

        value_result = evaluate_value_bet(
            probability=probability,
            bookmaker_odds=bookmaker_odds[market],
            minimum_edge=minimum_edge,
        )

        results.append(
            MarketValueBet(
                market=market,
                result=value_result,
            )
        )

    results.sort(
        key=lambda item: item.result.expected_value,
        reverse=True,
    )

    return results


def print_market_value_bets(
    results: List[MarketValueBet],
    bankroll: float,
    only_value_bets: bool = True,
    minimum_stake: float = 2.0,
    maximum_fraction: float = 0.03,
) -> None:
    print()
    print("BETLAB AI MARKET VALUE ANALYSIS")
    print("=" * 60)
    print(f"Bankroll:           €{bankroll:.2f}")

    displayed = 0

    for item in results:
        if only_value_bets and not item.result.is_value:
            continue

        displayed += 1

        stake = calculate_stake(
            bankroll=bankroll,
            stake_fraction=item.result.half_kelly,
            minimum_stake=minimum_stake,
            maximum_fraction=maximum_fraction,
        )

        print()
        print(item.market.upper())
        print("-" * 60)

        print(
            f"Probability:        "
            f"{item.result.probability:.2%}"
        )
        print(
            f"Fair odds:          "
            f"{item.result.fair_odds:.2f}"
        )
        print(
            f"Bookmaker odds:     "
            f"{item.result.bookmaker_odds:.2f}"
        )
        print(
            f"Edge:               "
            f"{item.result.edge:.2%}"
        )
        print(
            f"Expected value:     "
            f"{item.result.expected_value:.2%}"
        )
        print(
            f"Half Kelly:         "
            f"{item.result.half_kelly:.2%}"
        )

        print(
            f"Kelly stake:        "
            f"€{stake.recommended_stake:.2f}"
        )
        print(
            f"Final stake:        "
            f"€{stake.final_stake:.2f}"
        )

        if stake.capped:
            print("Stake capped:       YES")
        else:
            print("Stake capped:       NO")

        if stake.skipped:
            print("Stake skipped:      YES")
        else:
            print("Stake skipped:      NO")

        if stake.reason:
            print(
                f"Stake reason:       "
                f"{stake.reason}"
            )

        print(
            f"Value bet:          "
            f"{'YES' if item.result.is_value else 'NO'}"
        )

    if displayed == 0:
        print()
        print("No value bets found.")


def print_value_bet(
    result: ValueBetResult,
) -> None:
    print()
    print("BETLAB AI VALUE BET")
    print("=" * 50)

    print(
        f"Probability:        "
        f"{result.probability:.2%}"
    )
    print(
        f"Fair odds:          "
        f"{result.fair_odds:.2f}"
    )
    print(
        f"Bookmaker odds:     "
        f"{result.bookmaker_odds:.2f}"
    )

    print()
    print(
        f"Edge:               "
        f"{result.edge:.2%}"
    )
    print(
        f"Expected value:     "
        f"{result.expected_value:.2%}"
    )

    print()
    print(
        f"Full Kelly:         "
        f"{result.kelly_fraction:.2%}"
    )
    print(
        f"Half Kelly:         "
        f"{result.half_kelly:.2%}"
    )
    print(
        f"Quarter Kelly:      "
        f"{result.quarter_kelly:.2%}"
    )

    print()
    print(
        f"Value bet:          "
        f"{'YES' if result.is_value else 'NO'}"
    )


def main() -> None:
    from models.prediction_engine import predict_match

    bankroll = 100.0

    prediction = predict_match(
        home_team_id=18,
        away_team_id=3,
        league_id=1,
        season_id=1,
        use_dixon_coles=True,
    )

    bookmaker_odds = {
        "home_win": 1.50,
        "draw": 5.80,
        "away_win": 16.00,

        "over_15": 1.35,
        "under_15": 3.20,

        "over_25": 1.95,
        "under_25": 1.95,

        "over_35": 3.30,
        "under_35": 1.35,

        "btts_yes": 2.55,
        "btts_no": 1.60,
    }

    results = evaluate_prediction_markets(
        prediction=prediction,
        bookmaker_odds=bookmaker_odds,
        minimum_edge=0.02,
    )

    print_market_value_bets(
        results=results,
        bankroll=bankroll,
        only_value_bets=False,
        minimum_stake=2.0,
        maximum_fraction=0.03,
    )


if __name__ == "__main__":
    main()