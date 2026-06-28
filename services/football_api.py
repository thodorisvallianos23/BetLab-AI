from datetime import date


def get_today_fixtures():
    """
    Temporary mock data.
    Later this will connect to a real football API.
    """

    return [
        {
            "date": str(date.today()),
            "league": "Premier League",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
        },
        {
            "date": str(date.today()),
            "league": "Premier League",
            "home_team": "Liverpool",
            "away_team": "Aston Villa",
        },
        {
            "date": str(date.today()),
            "league": "Premier League",
            "home_team": "Man City",
            "away_team": "Tottenham",
        },
    ]