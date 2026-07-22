from services.league_importer import import_league


TOP_LEAGUES = [
    "PL",   # Premier League
    "PD",   # La Liga
    "SA",   # Serie A
    "BL1",  # Bundesliga
    "FL1",  # Ligue 1
    "ELC",  # Championship
    "DED",  # Eredivisie
    "PPL",  # Primeira Liga
]


def import_all_leagues():
    total_downloaded = 0
    total_inserted = 0
    total_skipped = 0

    for competition_code in TOP_LEAGUES:
        try:
            result = import_league(competition_code)

            total_downloaded += result["downloaded"]
            total_inserted += result["inserted"]
            total_skipped += result["skipped"]

        except Exception as error:
            print(f"❌ Failed to import {competition_code}: {error}")

    print()
    print("===== ALL LEAGUES COMPLETE =====")
    print(f"Downloaded: {total_downloaded}")
    print(f"Inserted:   {total_inserted}")
    print(f"Skipped:    {total_skipped}")


if __name__ == "__main__":
    import_all_leagues()