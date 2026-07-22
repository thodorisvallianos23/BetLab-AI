from dataclasses import dataclass
from typing import Any

from models.todays_picks_engine import get_todays_picks


@dataclass(frozen=True)
class DashboardStats:
    todays_matches: int
    value_bets: int
    portfolio_bets: int
    bankroll: float
    expected_roi: float


class DashboardController:

    def get_today_picks(self, limit: int = 50) -> list[dict[str, Any]]:
        try:
            picks = get_todays_picks(
                limit=limit,
                include_passes=True,
            )

            print(f"Loaded {len(picks)} picks")

            return picks

        except Exception as error:
            print("Dashboard loading error:")
            print(error)
            return []

    def get_dashboard_stats(
        self,
        bankroll: float = 1000.0,
    ) -> DashboardStats:

        picks = self.get_today_picks()

        value_picks = [
            pick
            for pick in picks
            if pick.get("recommendation_status") == "VALUE"
        ]

        portfolio_picks = [
            pick
            for pick in value_picks
            if float(pick.get("suggested_stake", 0.0)) > 0.0
        ]

        expected_roi = 0.0

        if value_picks:
            expected_roi = sum(
                float(pick.get("expected_value_percent", 0.0))
                for pick in value_picks
            ) / len(value_picks)

        return DashboardStats(
            todays_matches=len(picks),
            value_bets=len(value_picks),
            portfolio_bets=len(portfolio_picks),
            bankroll=bankroll,
            expected_roi=expected_roi,
        )