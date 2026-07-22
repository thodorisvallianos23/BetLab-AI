import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "betlab_v2.db"
)


def get_connection() -> sqlite3.Connection:
    """
    Returns a SQLite connection
    to the BetLab database.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def main() -> None:
    connection = get_connection()

    print()
    print("DATABASE CONNECTION")
    print("-" * 55)
    print("Connection successful.")

    connection.close()


if __name__ == "__main__":
    main()
