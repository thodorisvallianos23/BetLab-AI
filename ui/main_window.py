from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from ui.pages.analysis import AnalysisPage
from ui.pages.backtesting import BacktestingPage
from ui.pages.dashboard import DashboardPage
from ui.pages.history import HistoryPage
from ui.pages.settings import SettingsPage
from ui.pages.value_bets import ValueBetsPage
from ui.widgets.sidebar import Sidebar
from ui.pages.betting_slip import BettingSlipPage

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("BETLAB AI")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.pages.setObjectName("pageStack")
        root_layout.addWidget(self.pages, 1)

        self.page_indexes: dict[str, int] = {}

        self.add_page("dashboard", DashboardPage())
        self.add_page("analysis", AnalysisPage())
        self.add_page("value_bets", ValueBetsPage())
        self.add_page("betting_slip", BettingSlipPage())
        self.add_page("backtesting", BacktestingPage())
        self.add_page("history", HistoryPage())
        self.add_page("settings", SettingsPage())

        self.sidebar.page_selected.connect(self.change_page)

        self.change_page("dashboard")

    def add_page(self, page_name: str, page: QWidget) -> None:
        index = self.pages.addWidget(page)
        self.page_indexes[page_name] = index

    def change_page(self, page_name: str) -> None:
        index = self.page_indexes.get(page_name)

        if index is None:
            return

        self.pages.setCurrentIndex(index)