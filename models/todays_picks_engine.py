from database.bankroll import calculate_suggested_stake
from models.prediction_engine import predict_match
from services.football_api import get_today_fixtures
from services.odds_api import (
    compare_odds_with_model,
    extract_match_odds,
    extract_totals_odds,
    get_live_odds,
)


TEAM_NAME_MAP = {
    "United States": "USA",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cape Verde",
}


MARKET_CONFIG = [
    {
        "market": "Home Win",
        "probability_key": "home_win",
        "minimum_probability": 0.46,
    },
    {
        "market": "Draw",
        "probability_key": "draw",
        "minimum_probability": 0.30,
    },
    {
        "market": "Away Win",
        "probability_key": "away_win",
        "minimum_probability": 0.46,
    },
    {
        "market": "Over 1.5",
        "probability_key": "over_15",
        "minimum_probability": 0.68,
    },
    {
        "market": "Over 2.5",
        "probability_key": "over_25",
        "minimum_probability": 0.50,
    },
    {
        "market": "Over 3.5",
        "probability_key": "over_35",
        "minimum_probability": 0.34,
    },
]


def normalize_team_name(name):
    return TEAM_NAME_MAP.get(name, name)


def explain_pick(prediction, recommendation_status, market=None):
    reasons = []

    if recommendation_status == "PASS":
        reasons.append(
            "🟡 Κανένα market δεν πέρασε τα ελάχιστα όρια αξιοπιστίας."
        )
        reasons.append(
            "ℹ️ Το μοντέλο προτείνει αποχή αντί για αδύναμο στοίχημα."
        )
        return reasons

    if prediction["confidence"] >= 65:
        reasons.append("✅ Strong AI confidence")

    if prediction["total_xg"] >= 2.7:
        reasons.append("✅ High projected total xG")

    if prediction["home_form"] >= 65:
        reasons.append("✅ Home team is in good form")

    if prediction["btts"] >= 0.55:
        reasons.append("✅ Both teams likely to score")

    if market:
        reasons.append(f"📊 Best scanned market: {market}")

    if recommendation_status == "VALUE":
        reasons.append(
            "💎 Positive expected value detected against live odds"
        )

    if recommendation_status == "NO_VALUE":
        reasons.append(
            "ℹ️ Model signal found, but current odds do not offer enough value"
        )

    if not reasons:
        reasons.append("ℹ️ Moderate model signal")

    return reasons


def find_odds_event(live_odds, home_team, away_team):
    normalized_home = normalize_team_name(home_team)
    normalized_away = normalize_team_name(away_team)

    for event in live_odds:
        event_home = event.get("home_team")
        event_away = event.get("away_team")

        same_direction = (
            event_home == normalized_home
            and event_away == normalized_away
        )

        reverse_direction = (
            event_home == normalized_away
            and event_away == normalized_home
        )

        if same_direction or reverse_direction:
            return event

    return None


def get_market_odds(
    event,
    market,
    prediction,
    home_team,
    away_team,
):
    if market == "Over 1.5":
        return (
            extract_totals_odds(
                event,
                point=1.5,
                outcome_name="Over",
            ),
            prediction["over_15"],
        )

    if market == "Over 2.5":
        return (
            extract_totals_odds(
                event,
                point=2.5,
                outcome_name="Over",
            ),
            prediction["over_25"],
        )

    if market == "Over 3.5":
        return (
            extract_totals_odds(
                event,
                point=3.5,
                outcome_name="Over",
            ),
            prediction["over_35"],
        )

    if market == "Home Win":
        return (
            extract_match_odds(
                event,
                normalize_team_name(home_team),
            ),
            prediction["home_win"],
        )

    if market == "Away Win":
        return (
            extract_match_odds(
                event,
                normalize_team_name(away_team),
            ),
            prediction["away_win"],
        )

    if market == "Draw":
        return (
            extract_match_odds(
                event,
                "Draw",
            ),
            prediction["draw"],
        )

    return [], 0.0


def get_fair_odds_for_market(prediction, market):
    fair_odds_map = {
        "Home Win": prediction["fair_home_win"],
        "Draw": prediction["fair_draw"],
        "Away Win": prediction["fair_away_win"],
        "Over 1.5": prediction["fair_o15"],
        "Over 2.5": prediction["fair_o25"],
        "Over 3.5": prediction["fair_o35"],
    }

    return float(fair_odds_map.get(market, 0.0))


def get_qualified_markets(prediction):
    qualified = []

    for config in MARKET_CONFIG:
        probability = float(
            prediction[config["probability_key"]]
        )

        minimum_probability = float(
            config["minimum_probability"]
        )

        if probability < minimum_probability:
            continue

        qualified.append(
            {
                "market": config["market"],
                "probability": probability,
                "fair_odds": get_fair_odds_for_market(
                    prediction,
                    config["market"],
                ),
                "probability_edge": (
                    probability - minimum_probability
                ),
            }
        )

    return qualified


def scan_value_markets(
    event,
    prediction,
    home_team,
    away_team,
):
    qualified_markets = get_qualified_markets(prediction)
    scanned_markets = []

    for candidate in qualified_markets:
        market = candidate["market"]

        odds_rows, model_probability = get_market_odds(
            event,
            market,
            prediction,
            home_team,
            away_team,
        )

        if not odds_rows:
            continue

        value_rows = compare_odds_with_model(
            model_probability,
            odds_rows,
        )

        if not value_rows:
            continue

        best_market_value = value_rows[0]

        scanned_markets.append(
            {
                "market": market,
                "probability": model_probability,
                "fair_odds": candidate["fair_odds"],
                "probability_edge": candidate["probability_edge"],
                "bookmaker": best_market_value["bookmaker"],
                "odds": float(best_market_value["odds"]),
                "value_percent": float(
                    best_market_value["value_percent"]
                ),
                "expected_value_percent": float(
                    best_market_value.get(
                        "expected_value_percent",
                        0.0,
                    )
                ),
                "kelly_percent": float(
                    best_market_value.get(
                        "kelly_percent",
                        0.0,
                    )
                ),
                "quarter_kelly_percent": float(
                    best_market_value.get(
                        "quarter_kelly_percent",
                        0.0,
                    )
                ),
                "is_value": bool(
                    best_market_value["is_value"]
                ),
            }
        )

    scanned_markets.sort(
        key=lambda item: (
            item["is_value"],
            item["expected_value_percent"],
            item["value_percent"],
            item["probability_edge"],
        ),
        reverse=True,
    )

    return scanned_markets


def build_pass_pick(fixture, prediction):
    home_team = fixture["home_team"]
    away_team = fixture["away_team"]

    return {
        "date": fixture["date"],
        "league": fixture["league"],
        "match": f"{home_team} vs {away_team}",
        "market": "PASS / NO BET",
        "probability": 0.0,
        "fair_odds": 0.0,
        "confidence": prediction["confidence"],
        "stars": prediction["stars"],
        "best_bookmaker": "N/A",
        "best_odds": 0.0,
        "value_percent": 0.0,
        "expected_value_percent": 0.0,
        "kelly_percent": 0.0,
        "quarter_kelly_percent": 0.0,
        "suggested_stake": 0.0,
        "is_value": False,
        "recommendation_status": "PASS",
        "odds_available": False,
        "explanation": explain_pick(
            prediction,
            "PASS",
        ),
    }


def build_no_value_pick(
    fixture,
    prediction,
    candidate,
):
    home_team = fixture["home_team"]
    away_team = fixture["away_team"]

    return {
        "date": fixture["date"],
        "league": fixture["league"],
        "match": f"{home_team} vs {away_team}",
        "market": candidate["market"],
        "probability": candidate["probability"],
        "fair_odds": candidate["fair_odds"],
        "confidence": prediction["confidence"],
        "stars": prediction["stars"],
        "best_bookmaker": candidate["bookmaker"],
        "best_odds": candidate["odds"],
        "value_percent": candidate["value_percent"],
        "expected_value_percent": candidate[
            "expected_value_percent"
        ],
        "kelly_percent": candidate["kelly_percent"],
        "quarter_kelly_percent": candidate[
            "quarter_kelly_percent"
        ],
        "suggested_stake": 0.0,
        "is_value": False,
        "recommendation_status": "NO_VALUE",
        "odds_available": True,
        "explanation": explain_pick(
            prediction,
            "NO_VALUE",
            candidate["market"],
        ),
    }


def build_value_pick(
    fixture,
    prediction,
    candidate,
):
    home_team = fixture["home_team"]
    away_team = fixture["away_team"]

    suggested_stake = calculate_suggested_stake(
        candidate["quarter_kelly_percent"]
    )

    return {
        "date": fixture["date"],
        "league": fixture["league"],
        "match": f"{home_team} vs {away_team}",
        "market": candidate["market"],
        "probability": candidate["probability"],
        "fair_odds": candidate["fair_odds"],
        "confidence": prediction["confidence"],
        "stars": prediction["stars"],
        "best_bookmaker": candidate["bookmaker"],
        "best_odds": candidate["odds"],
        "value_percent": candidate["value_percent"],
        "expected_value_percent": candidate[
            "expected_value_percent"
        ],
        "kelly_percent": candidate["kelly_percent"],
        "quarter_kelly_percent": candidate[
            "quarter_kelly_percent"
        ],
        "suggested_stake": suggested_stake,
        "is_value": True,
        "recommendation_status": "VALUE",
        "odds_available": True,
        "explanation": explain_pick(
            prediction,
            "VALUE",
            candidate["market"],
        ),
    }


def get_todays_picks(
    limit=10,
    include_passes=True,
):
    live_odds = get_live_odds()
    picks = []

    print(f"Processing {len(live_odds)} odds events")

    for event in live_odds:
        home_team = event.get("home_team")
        away_team = event.get("away_team")

        if not home_team or not away_team:
            continue

        print(f"Checking: {home_team} vs {away_team}")

        # Προσωρινά δεν καλούμε ακόμη το prediction engine,
        # επειδή χρειάζεται database IDs και όχι ονόματα.
        fixture = {
            "date": event.get("commence_time", ""),
            "league": event.get(
                "sport_title",
                event.get("sport_key", "Unknown"),
            ),
            "home_team": home_team,
            "away_team": away_team,
        }

        picks.append(
            {
                "date": fixture["date"],
                "league": fixture["league"],
                "match": f"{home_team} vs {away_team}",
                "market": "PENDING MODEL",
                "probability": 0.0,
                "fair_odds": 0.0,
                "confidence": 0.0,
                "stars": 0,
                "best_bookmaker": "N/A",
                "best_odds": 0.0,
                "value_percent": 0.0,
                "expected_value_percent": 0.0,
                "kelly_percent": 0.0,
                "quarter_kelly_percent": 0.0,
                "suggested_stake": 0.0,
                "is_value": False,
                "recommendation_status": "PASS",
                "odds_available": bool(event.get("bookmakers")),
                "explanation": [
                    "ℹ️ Odds event loaded successfully.",
                    "ℹ️ Waiting for team and league database mapping.",
                ],
            }
        )

    return picks[:limit]