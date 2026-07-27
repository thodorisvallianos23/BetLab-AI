import os
from pathlib import Path

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

ODDS_API_KEY = os.getenv("ODDS_API_KEY")


SOCCER_SPORTS = [
    "soccer_argentina_primera_division",
    "soccer_austria_bundesliga",
    "soccer_belgium_first_div",
    "soccer_brazil_campeonato",
    "soccer_brazil_serie_b",
    "soccer_chile_campeonato",
    "soccer_china_superleague",
    "soccer_conmebol_copa_libertadores",
    "soccer_conmebol_copa_sudamericana",
    "soccer_denmark_superliga",
    "soccer_efl_champ",
    "soccer_england_efl_cup",
    "soccer_england_league1",
    "soccer_england_league2",
    "soccer_epl",
    "soccer_finland_veikkausliiga",
    "soccer_france_ligue_one",
    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",
    "soccer_germany_dfb_pokal",
    "soccer_germany_liga3",
    "soccer_greece_super_league",
    "soccer_italy_serie_a",
    "soccer_korea_kleague1",
    "soccer_league_of_ireland",
    "soccer_mexico_ligamx",
    "soccer_netherlands_eredivisie",
    "soccer_norway_eliteserien",
    "soccer_poland_ekstraklasa",
    "soccer_russia_premier_league",
    "soccer_spain_la_liga",
    "soccer_spl",
    "soccer_sweden_allsvenskan",
    "soccer_sweden_superettan",
    "soccer_switzerland_superleague",
    "soccer_uefa_champs_league_qualification",
    "soccer_usa_mls",
]


def get_live_odds():
    return [
        {
            "id": "mock_1",
            "sport_key": "soccer_epl",
            "sport_title": "Premier League",
            "commence_time": "2026-07-27T18:00:00Z",
            "home_team": "Arsenal FC",
            "away_team": "Liverpool FC",
            "bookmakers": [
                {
                    "title": "Bet365",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {
                                    "name": "Arsenal FC",
                                    "price": 2.20,
                                },
                                {
                                    "name": "Draw",
                                    "price": 3.40,
                                },
                                {
                                    "name": "Liverpool FC",
                                    "price": 3.10,
                                },
                            ],
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {
                                    "name": "Over",
                                    "point": 2.5,
                                    "price": 1.90,
                                },
                                {
                                    "name": "Under",
                                    "point": 2.5,
                                    "price": 1.95,
                                },
                            ],
                        },
                    ],
                },
                {
                    "title": "Novibet",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {
                                    "name": "Arsenal FC",
                                    "price": 2.25,
                                },
                                {
                                    "name": "Draw",
                                    "price": 3.35,
                                },
                                {
                                    "name": "Liverpool FC",
                                    "price": 3.05,
                                },
                            ],
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {
                                    "name": "Over",
                                    "point": 2.5,
                                    "price": 1.92,
                                },
                                {
                                    "name": "Under",
                                    "point": 2.5,
                                    "price": 1.93,
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    ]

def get_mock_bookmaker_odds(match_name, market):
    return [
        {
            "bookmaker": "Bet365",
            "market": market,
            "odds": 1.95,
        },
        {
            "bookmaker": "Stoiximan",
            "market": market,
            "odds": 1.88,
        },
        {
            "bookmaker": "Novibet",
            "market": market,
            "odds": 1.92,
        },
        {
            "bookmaker": "Betsson",
            "market": market,
            "odds": 1.90,
        },
        {
            "bookmaker": "Fonbet",
            "market": market,
            "odds": 1.86,
        },
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
                            "odds": outcome.get(
                                "price",
                                0,
                            ),
                        }
                    )

    rows.sort(
        key=lambda item: item["odds"],
        reverse=True,
    )

    return rows


def extract_totals_odds(
    event,
    point=2.5,
    outcome_name="Over",
):
    rows = []

    for bookmaker in event.get("bookmakers", []):
        title = bookmaker.get("title", "Unknown")

        for market in bookmaker.get("markets", []):
            if market.get("key") != "totals":
                continue

            for outcome in market.get("outcomes", []):
                outcome_point = float(
                    outcome.get("point", 0)
                )

                if (
                    outcome.get("name") == outcome_name
                    and outcome_point == float(point)
                ):
                    rows.append(
                        {
                            "bookmaker": title,
                            "market": (
                                f"{outcome_name} {point}"
                            ),
                            "selection": outcome_name,
                            "odds": outcome.get(
                                "price",
                                0,
                            ),
                        }
                    )

    rows.sort(
        key=lambda item: item["odds"],
        reverse=True,
    )

    return rows


def compare_odds_with_model(
    model_probability,
    bookmaker_odds,
):
    fair_odds = (
        1 / model_probability
        if model_probability > 0
        else 0
    )

    rows = []

    for item in bookmaker_odds:
        odds = float(item["odds"])

        if odds <= 1:
            continue

        if fair_odds > 0 and odds > fair_odds * 2:
            continue

        implied_probability = 1 / odds
        edge = model_probability - implied_probability

        expected_value = (
            model_probability * (odds - 1)
            - (1 - model_probability)
        )

        decimal_profit = odds - 1

        if decimal_profit > 0:
            kelly_fraction = (
                decimal_profit * model_probability
                - (1 - model_probability)
            ) / decimal_profit
        else:
            kelly_fraction = 0

        kelly_fraction = max(
            0,
            kelly_fraction,
        )

        rows.append(
            {
                "bookmaker": item["bookmaker"],
                "market": item["market"],
                "selection": item.get(
                    "selection",
                    "",
                ),
                "odds": odds,
                "fair_odds": fair_odds,
                "implied_probability": (
                    implied_probability
                ),
                "edge": edge,
                "value_percent": edge * 100,
                "expected_value": expected_value,
                "expected_value_percent": (
                    expected_value * 100
                ),
                "kelly_fraction": kelly_fraction,
                "kelly_percent": (
                    kelly_fraction * 100
                ),
                "quarter_kelly_percent": (
                    kelly_fraction * 25
                ),
                "is_value": (
                    edge > 0.03
                    and expected_value > 0
                ),
            }
        )

    rows.sort(
        key=lambda item: item["expected_value"],
        reverse=True,
    )

    return rows


def list_available_sports():
    if not ODDS_API_KEY:
        print("❌ ODDS_API_KEY not found.")
        return []

    url = "https://api.the-odds-api.com/v4/sports"

    try:
        response = requests.get(
            url,
            params={"apiKey": ODDS_API_KEY},
            timeout=15,
        )
    except requests.RequestException as error:
        print(f"❌ Sports request failed: {error}")
        return []

    print("Sports Status:", response.status_code)

    if response.status_code != 200:
        print(
            f"⚠️ HTTP {response.status_code}"
        )
        print(
            "API RESPONSE:",
            response.text,
        )
        return []

    try:
        data = response.json()
    except ValueError:
        print("❌ Invalid JSON response.")
        return []

    for sport in data:
        print(
            sport.get("key"),
            "|",
            sport.get("title"),
            "| active:",
            sport.get("active"),
        )

    return data