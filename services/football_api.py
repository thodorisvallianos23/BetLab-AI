import os
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

BASE_URL = "https://api.football-data.org/v4"


def _headers():
    return {
        "X-Auth-Token": API_KEY,
    }


def get_today_fixtures(days_ahead: int = 10):

    if not API_KEY:
        print("❌ FOOTBALL_DATA_API_KEY not found.")
        return []

    today = date.today()
    end_date = today + timedelta(days=days_ahead - 1)

    url = f"{BASE_URL}/competitions/CL/matches"

    params = {
        "dateFrom": today.isoformat(),
        "dateTo": end_date.isoformat(),
    }

    try:
        response = requests.get(
            url,
            headers=_headers(),
            params=params,
            timeout=15,
        )
    except requests.RequestException as error:
        print(error)
        return []

    print("Football API URL:", response.url)
    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return []

    data = response.json()

    matches = data.get("matches", [])

    fixtures = []

    for match in matches:

        home = match.get("homeTeam", {}).get("name")
        away = match.get("awayTeam", {}).get("name")

        if not home or not away:
            continue

        fixtures.append(
            {
                "date": match["utcDate"][:10],
                "league": match["competition"]["name"],
                "home_team": home,
                "away_team": away,
                "status": match["status"],
            }
        )

    print(f"✅ Loaded {len(fixtures)} valid fixtures")

    return fixtures


def get_competition_matches(
    competition_code,
    season=None,
):
    """
    Download and normalize all matches for a competition.

    Examples:
        get_competition_matches("PL")
        get_competition_matches("PD", season=2024)
    """

    if not API_KEY:
        print("❌ FOOTBALL_DATA_API_KEY not found.")
        return []

    url = f"{BASE_URL}/competitions/{competition_code}/matches"

    params = {}

    if season is not None:
        params["season"] = season

    try:
        response = requests.get(
            url,
            headers=_headers(),
            params=params,
            timeout=30,
        )
    except requests.RequestException as error:
        print(f"❌ Football API request failed: {error}")
        return []

    print(f"Competition: {competition_code}")
    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return []

    try:
        data = response.json()
    except ValueError:
        print("❌ Invalid JSON response.")
        return []

    raw_matches = data.get("matches", [])
    normalized_matches = []

    for match in raw_matches:
        competition = match.get("competition") or {}
        area = match.get("area") or {}
        season_data = match.get("season") or {}
        home_team = match.get("homeTeam") or {}
        away_team = match.get("awayTeam") or {}
        score = match.get("score") or {}
        full_time = score.get("fullTime") or {}

        utc_date = match.get("utcDate")
        home_name = home_team.get("name")
        away_name = away_team.get("name")

        if not utc_date or not home_name or not away_name:
            continue

        normalized_matches.append(
            {
                "external_match_id": match.get("id"),
                "match_date": utc_date[:10],
                "utc_date": utc_date,
                "league_name": competition.get("name"),
                "competition_code": competition.get(
                    "code",
                    competition_code,
                ),
                "country": area.get("name"),
                "season_start": season_data.get("startDate"),
                "season_end": season_data.get("endDate"),
                "home_team": home_name,
                "away_team": away_name,
                "home_goals": full_time.get("home"),
                "away_goals": full_time.get("away"),
                "status": match.get("status"),
            }
        )

    print(f"✅ Downloaded {len(normalized_matches)} matches")

    return normalized_matches