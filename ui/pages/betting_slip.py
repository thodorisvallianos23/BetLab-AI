from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class BettingSlipPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Betting Slip")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Manage selected bets and stakes")
        subtitle.setObjectName("pageSubtitle")

        content = QLabel("Betting Slip Page")
        content.setObjectName("contentLabel")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(content)
        layout.addStretch()