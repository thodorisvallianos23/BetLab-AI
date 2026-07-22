from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
)

from controllers.dashboard_controller import DashboardController
from ui.widgets.stats_card import StatsCard


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = DashboardController()
        stats = self.controller.get_dashboard_stats()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 30, 35, 30)
        main_layout.setSpacing(25)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Overview of today's betting opportunities")
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        ####################################################################
        # Statistics Cards
        ####################################################################

        cards = QGridLayout()
        cards.setHorizontalSpacing(18)
        cards.setVerticalSpacing(18)

        cards.addWidget(
            StatsCard(
                "Today's Matches",
                str(stats.todays_matches),
                "Scheduled matches",
            ),
            0,
            0,
        )

        cards.addWidget(
            StatsCard(
                "Value Bets",
                str(stats.value_bets),
                "Positive EV bets",
            ),
            0,
            1,
        )

        cards.addWidget(
            StatsCard(
                "Portfolio",
                str(stats.portfolio_bets),
                "Recommended bets",
            ),
            0,
            2,
        )

        cards.addWidget(
            StatsCard(
                "Bankroll",
                f"€{stats.bankroll:,.0f}",
                "Current bankroll",
            ),
            0,
            3,
        )

        roi_prefix = "+" if stats.expected_roi > 0 else ""

        cards.addWidget(
            StatsCard(
                "Expected ROI",
                f"{roi_prefix}{stats.expected_roi:.2f}%",
                "Average expected value",
            ),
            0,
            4,
        )

        main_layout.addLayout(cards)

        ####################################################################
        # Placeholder
        ####################################################################

        placeholder = QLabel("Today's Value Bets Table (coming next)")
        placeholder.setObjectName("contentLabel")

        main_layout.addStretch()
        main_layout.addWidget(placeholder)