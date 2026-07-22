from dataclasses import dataclass
from typing import Dict, List, Set

from models.betting_slip import BettingSlip, BettingSlipItem
from models.value_betting import MarketValueBet
from models.bankroll import calculate_stake


@dataclass(frozen=True)
class PortfolioRule:
    market: str
    group: str


MARKET_GROUPS: Dict[str, str] = {
    "home_win": "match_result",
    "draw": "match_result",
    "away_win": "match_result",

    "over_15": "totals",
    "under_15": "totals",
    "over_25": "totals",
    "under_25": "totals",
    "over_35": "totals",
    "under_35": "totals",

    "btts_yes": "btts",
    "btts_no": "btts",
}


def optimize_portfolio(
    results: List[MarketValueBet],
    bankroll: float,
    max_selections: int = 3,
    minimum_stake: float = 2.0,
    maximum_fraction: float = 0.03,
) -> BettingSlip:
    selections: List[BettingSlipItem] = []
    used_groups: Set[str] = set()

    for item in results:
        if not item.result.is_value:
            continue

        market_group = MARKET_GROUPS.get(
            item.market,
            item.market,
        )

        if market_group in used_groups:
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

        used_groups.add(market_group)

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


def main() -> None:
    from models.prediction_engine import predict_match
    from models.value_betting import evaluate_prediction_markets
    from models.betting_slip import print_betting_slip

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

    slip = optimize_portfolio(
        results=results,
        bankroll=bankroll,
        max_selections=3,
        minimum_stake=2.0,
        maximum_fraction=0.03,
    )

    print_betting_slip(slip)


if __name__ == "__main__":
    main()