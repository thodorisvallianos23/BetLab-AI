import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from services.odds_api import list_available_sports

list_available_sports()

def load_stylesheet() -> str:
    style_path = (
        Path(__file__).parent
        / "resources"
        / "styles"
        / "dark.qss"
    )

    try:
        return style_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()