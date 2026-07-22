from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Application settings")
        subtitle.setObjectName("pageSubtitle")

        content = QLabel("Settings Page")
        content.setObjectName("contentLabel")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(content)
        layout.addStretch()