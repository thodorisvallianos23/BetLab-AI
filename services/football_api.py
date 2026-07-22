import os
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

COMPETITION = "CL"  # Champions League
BASE_URL = f"https://api.football-data.org/v4/competitions/{COMPETITION}/matches"


def get_today_fixtures(days_ahead: int = 10):
    if not API_KEY:
        print("❌ FOOTBALL_DATA_API_KEY not found.")
        return []

    today = date.today()
    end_date = today + timedelta(days=days_ahead - 1)

    headers = {
        "X-Auth-Token": API_KEY,
    }

    params = {
        "dateFrom": today.isoformat(),
        "dateTo": end_date.isoformat(),
    }

    try:
        response = requests.get(
            BASE_URL,
            headers=headers,
            params=params,
            timeout=15,
        )
    except requests.RequestException as error:
        print(error)
        return []

    print("API KEY LOADED:", bool(API_KEY))
    print("Football API URL:", response.url)
    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return []

    data = response.json()
    print(data)
    matches = data.get("matches", [])

    print(f"Raw matches: {len(matches)}")

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