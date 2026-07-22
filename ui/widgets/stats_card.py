from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)


class StatsCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str,
        description: str = "",
    ) -> None:
        super().__init__()

        self.setObjectName("statsCard")
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statsCardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("statsCardValue")

        self.description_label = QLabel(description)
        self.description_label.setObjectName("statsCardDescription")
        self.description_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        if description:
            layout.addWidget(self.description_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

    def set_description(self, description: str) -> None:
        self.description_label.setText(description)
        self.description_label.setVisible(bool(description))