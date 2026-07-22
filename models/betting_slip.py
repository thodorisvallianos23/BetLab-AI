from dataclasses import dataclass
from typing import List

from models.bankroll import calculate_stake
from models.value_betting import MarketValueBet


@dataclass(frozen=True)
class BettingSlipItem:
    market: str
    probability: float
    bookmaker_odds: float
    expected_value: float
    stake: float


@dataclass(frozen=True)
class BettingSlip:
    bankroll: float
    selections: List[BettingSlipItem]
    total_stake: float
    average_expected_value: float


def generate_betting_slip(
    results: List[MarketValueBet],
    bankroll: float,
    max_selections: int = 3,
    minimum_stake: float = 2.0,
    maximum_fraction: float = 0.03,
) -> BettingSlip:
    selections: List[BettingSlipItem] = []

    for item in results:
        if not item.result.is_value:
            continue

        stake_result = calculate_stake(
            bankroll=bankroll,
            stake_fraction=item.result.half_kelly,
            minimum_stake=minimum_stake,
            maximum_fraction=maximum_fraction,
        )

        if stake_result.skipped:
            continue

        selections.append(
            BettingSlipItem(
                market=item.market,
                probability=item.result.probability,
                bookmaker_odds=item.result.bookmaker_odds,
                expected_value=item.result.expected_value,
                stake=stake_result.final_stake,
            )
        )

        if len(selections) >= max_selections:
            break

    total_stake = sum(
        item.stake
        for item in selections
    )

    if selections:
        average_expected_value = sum(
            item.expected_value
            for item in selections
        ) / len(selections)
    else:
        average_expected_value = 0.0

    return BettingSlip(
        bankroll=bankroll,
        selections=selections,
        total_stake=total_stake,
        average_expected_value=average_expected_value,
    )


def print_betting_slip(
    slip: BettingSlip,
) -> None:
    print()
    print("BETLAB AI BETTING SLIP")
    print("=" * 60)
    print(f"Bankroll:           €{slip.bankroll:.2f}")

    if not slip.selections:
        print()
        print("No playable value bets found.")
        return

    print()
    print("RECOMMENDED BETS")
    print("-" * 60)

    for index, item in enumerate(
        slip.selections,
        start=1,
    ):
        print()
        print(f"{index}. {item.market.upper()}")
        print(f"   Probability:     {item.probability:.2%}")
        print(f"   Odds:            {item.bookmaker_odds:.2f}")
        print(f"   Expected value:  {item.expected_value:.2%}")
        print(f"   Stake:           €{item.stake:.2f}")

    print()
    print("-" * 60)
    print(f"Total stake:        €{slip.total_stake:.2f}")
    print(
        f"Average EV:         "
        f"{slip.average_expected_value:.2%}"
    )


def main() -> None:
    from models.prediction_engine import predict_match
    from models.value_betting import evaluate_prediction_markets

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

    slip = generate_betting_slip(
        results=results,
        bankroll=bankroll,
        max_selections=3,
        minimum_stake=2.0,
        maximum_fraction=0.03,
    )

    print_betting_slip(slip)


if __name__ == "__main__":
    main()