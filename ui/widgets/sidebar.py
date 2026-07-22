from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Sidebar(QFrame):
    page_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(10)

        logo = QLabel("BETLAB AI")
        logo.setObjectName("logo")
        layout.addWidget(logo)

        subtitle = QLabel("Football Analytics")
        subtitle.setObjectName("logoSubtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(28)

        pages = [
            ("dashboard", "Dashboard"),
            ("analysis", "Match Analysis"),
            ("value_bets", "Value Bets"),
            ("betting_slip", "Betting Slip"),
            ("backtesting", "Backtesting"),
            ("history", "History"),
            ("settings", "Settings"),
        ]

        for page_name, button_text in pages:
            button = QPushButton(button_text)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(
                self.cursor().shape()
            )

            button.clicked.connect(
                lambda checked=False, name=page_name:
                self.select_page(name)
            )

            layout.addWidget(button)
            self._buttons[page_name] = button

        layout.addStretch()

        version = QLabel("Version 1.0")
        version.setObjectName("versionLabel")
        layout.addWidget(version)

        self.select_page("dashboard")

    def select_page(self, page_name: str) -> None:
        if page_name not in self._buttons:
            return

        for name, button in self._buttons.items():
            button.setChecked(name == page_name)

        self.page_selected.emit(page_name)