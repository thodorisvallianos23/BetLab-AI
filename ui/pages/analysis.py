from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AnalysisPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Match Analysis")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Analyze upcoming football matches")
        subtitle.setObjectName("pageSubtitle")

        content = QLabel("Analysis Page")
        content.setObjectName("contentLabel")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(content)
        layout.addStretch()