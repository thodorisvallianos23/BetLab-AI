from database.connection import get_connection


TEAM_MERGES = {
    64: 18,    # Arsenal FC -> Arsenal
    79: 3,     # Aston Villa FC -> Aston Villa
    74: 16,    # Brentford FC -> Brentford
    160: 10,   # Burnley FC -> Burnley
    83: 13,    # Chelsea FC -> Chelsea
    73: 14,    # Crystal Palace FC -> Crystal Palace
    72: 20,    # Everton FC -> Everton
    82: 6,     # Fulham FC -> Fulham
    81: 1,     # Liverpool FC -> Liverpool
    69: 7,     # Sunderland AFC -> Sunderland
}


def main():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON")

        for duplicate_id, canonical_id in TEAM_MERGES.items():
            cursor.execute(
                """
                SELECT team_name
                FROM teams
                WHERE id = ?
                """,
                (duplicate_id,),
            )
            duplicate = cursor.fetchone()

            cursor.execute(
                """
                SELECT team_name
                FROM teams
                WHERE id = ?
                """,
                (canonical_id,),
            )
            canonical = cursor.fetchone()

            if duplicate is None:
                print(
                    f"Skipping duplicate ID {duplicate_id}: "
                    "team not found."
                )
                continue

            if canonical is None:
                raise ValueError(
                    f"Canonical team ID {canonical_id} not found."
                )

            print(
                f'Merging {duplicate["team_name"]} '
                f'({duplicate_id}) -> '
                f'{canonical["team_name"]} '
                f'({canonical_id})'
            )

            cursor.execute(
                """
                UPDATE matches
                SET home_team_id = ?
                WHERE home_team_id = ?
                """,
                (canonical_id, duplicate_id),
            )

            home_updates = cursor.rowcount

            cursor.execute(
                """
                UPDATE matches
                SET away_team_id = ?
                WHERE away_team_id = ?
                """,
                (canonical_id, duplicate_id),
            )

            away_updates = cursor.rowcount

            cursor.execute(
                """
                DELETE FROM teams
                WHERE id = ?
                """,
                (duplicate_id,),
            )

            print(
                f"  Home matches updated: {home_updates}"
            )
            print(
                f"  Away matches updated: {away_updates}"
            )
            print("  Duplicate team deleted.")

        connection.commit()
        print("\nMerge completed successfully.")

    except Exception:
        connection.rollback()
        print("\nMerge failed. Database changes rolled back.")
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()