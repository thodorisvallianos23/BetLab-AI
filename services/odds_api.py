import os
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

ODDS_API_KEY = os.getenv("ODDS_API_KEY")


def get_live_odds(sport="soccer_fifa_world_cup"):
    if not ODDS_API_KEY:
        print("❌ ODDS_API_KEY not found.")
        return []

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h,totals",
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params)

    print("Odds API Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return []

    return response.json()


def get_mock_bookmaker_odds(match_name, market):
    return [
        {"bookmaker": "Bet365", "market": market, "odds": 1.95},
        {"bookmaker": "Stoiximan", "market": market, "odds": 1.88},
        {"bookmaker": "Novibet", "market": market, "odds": 1.92},
        {"bookmaker": "Betsson", "market": market, "odds": 1.90},
        {"bookmaker": "Fonbet", "market": market, "odds": 1.86},
    ]


def extract_match_odds(event, selection):
    rows = []

    for bookmaker in event.get("bookmakers", []):
        title = bookmaker.get("title", "Unknown")

        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue

            for outcome in market.get("outcomes", []):
                if outcome.get("name") == selection:
                    rows.append(
                        {
                            "bookmaker": title,
                            "market": "Match Result",
                            "selection": selection,
                            "odds": outcome.get("price", 0),
                        }
                    )

    rows.sort(key=lambda x: x["odds"], reverse=True)
    return rows


def extract_totals_odds(event, point=2.5, outcome_name="Over"):
    rows = []

    for bookmaker in event.get("bookmakers", []):
        title = bookmaker.get("title", "Unknown")

        for market in bookmaker.get("markets", []):
            if market.get("key") != "totals":
                continue

            for outcome in market.get("outcomes", []):
                if (
                    outcome.get("name") == outcome_name
                    and float(outcome.get("point", 0)) == float(point)
                ):
                    rows.append(
                        {
                            "bookmaker": title,
                            "market": f"{outcome_name} {point}",
                            "selection": outcome_name,
                            "odds": outcome.get("price", 0),
                        }
                    )

    rows.sort(key=lambda x: x["odds"], reverse=True)
    return rows


def compare_odds_with_model(model_probability, bookmaker_odds):
    fair_odds = 1 / model_probability if model_probability > 0 else 0
    rows = []

    for item in bookmaker_odds:
        odds = item["odds"]

        if odds <= 1:
            continue

        if fair_odds > 0 and odds > fair_odds * 2:
            continue

        implied_probability = 1 / odds
        edge = model_probability - implied_probability

        rows.append(
            {
                "bookmaker": item["bookmaker"],
                "market": item["market"],
                "selection": item.get("selection", ""),
                "odds": odds,
                "fair_odds": fair_odds,
                "edge": edge,
                "value_percent": edge * 100,
                "is_value": edge > 0.05,
            }
        )

    rows.sort(key=lambda x: x["edge"], reverse=True)
    return rows