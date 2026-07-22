from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("History")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Previous bets and results")
        subtitle.setObjectName("pageSubtitle")

        content = QLabel("History Page")
        content.setObjectName("contentLabel")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(content)
        layout.addStretch()