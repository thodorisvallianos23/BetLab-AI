from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class BacktestingPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Backtesting")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Historical strategy performance")
        subtitle.setObjectName("pageSubtitle")

        content = QLabel("Backtesting Page")
        content.setObjectName("contentLabel")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(content)
        layout.addStretch()