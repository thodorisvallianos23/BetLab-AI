import os
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

today = date.today()
next_week = today + timedelta(days=7)

URL = (
    "https://api.football-data.org/v4/competitions/WC/matches"
    f"?dateFrom={today}&dateTo={next_week}"
)


def get_today_fixtures():
    if not API_KEY:
        print("❌ FOOTBALL_DATA_API_KEY not found.")
        return []

    headers = {
        "X-Auth-Token": API_KEY,
    }

    response = requests.get(URL, headers=headers)

    print("API KEY LOADED:", bool(API_KEY))
    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return []

    data = response.json()
    fixtures = []

    for match in data.get("matches", []):
        fixtures.append(
            {
                "date": match["utcDate"][:10],
                "league": match["competition"]["name"],
                "home_team": match["homeTeam"]["name"],
                "away_team": match["awayTeam"]["name"],
            }
        )

    print(f"✅ Loaded {len(fixtures)} fixtures")

    return fixtures