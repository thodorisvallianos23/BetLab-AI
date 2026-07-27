from database.bankroll import calculate_suggested_stake
from models.prediction_engine import predict_match
from services.odds_api import (
    compare_odds_with_model,
    extract_match_odds,
    extract_totals_odds,
    get_live_odds,
)
from dataclasses import asdict

from services.match_resolver import resolve_match

TEAM_NAME_MAP = {
    "United States": "USA",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cape Verde",
}


# Temporary model season used while live 2026/27 data is unavailable.
MODEL_SEASON_NAME = "2025/26"


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

    if prediction.get("confidence", 0.0) >= 65:
        reasons.append("✅ Strong AI confidence")

    if prediction.get("total_xg", 0.0) >= 2.7:
        reasons.append("✅ High projected total xG")

    if prediction.get("btts", 0.0) >= 0.55:
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

def prediction_to_dict(prediction_result):
    """
    Convert PredictionResult into the legacy dictionary keys used by
    the Today's Picks market scanner and dashboard.
    """
    prediction = asdict(prediction_result)

    strongest_probability = max(
        prediction["home_win_probability"],
        prediction["draw_probability"],
        prediction["away_win_probability"],
        prediction["over_15_probability"],
        prediction["over_25_probability"],
        prediction["over_35_probability"],
        prediction["btts_yes_probability"],
    )

    confidence = strongest_probability * 100
    stars = max(1, min(5, round(confidence / 20)))

    prediction.update(
        {
            "home_xg": prediction["home_expected_goals"],
            "away_xg": prediction["away_expected_goals"],
            "total_xg": prediction["total_expected_goals"],

            "home_win": prediction["home_win_probability"],
            "draw": prediction["draw_probability"],
            "away_win": prediction["away_win_probability"],

            "over_15": prediction["over_15_probability"],
            "under_15": prediction["under_15_probability"],
            "over_25": prediction["over_25_probability"],
            "under_25": prediction["under_25_probability"],
            "over_35": prediction["over_35_probability"],
            "under_35": prediction["under_35_probability"],

            "btts": prediction["btts_yes_probability"],
            "btts_yes": prediction["btts_yes_probability"],
            "btts_no": prediction["btts_no_probability"],

            "fair_home_win": prediction["fair_home_odds"],
            "fair_draw": prediction["fair_draw_odds"],
            "fair_away_win": prediction["fair_away_odds"],

            "fair_o15": prediction["fair_over_15_odds"],
            "fair_u15": prediction["fair_under_15_odds"],
            "fair_o25": prediction["fair_over_25_odds"],
            "fair_u25": prediction["fair_under_25_odds"],
            "fair_o35": prediction["fair_over_35_odds"],
            "fair_u35": prediction["fair_under_35_odds"],

            "fair_btts_yes": prediction["fair_btts_yes_odds"],
            "fair_btts_no": prediction["fair_btts_no_odds"],

            "confidence": confidence,
            "stars": stars,
        }
    )

    return prediction


def get_todays_picks(
    limit=10,
    include_passes=True,
):
    live_odds = get_live_odds()
    picks = []

    print(f"LIVE ODDS FOUND: {len(live_odds)}")
    print(f"Processing {len(live_odds)} odds events")

    for event in live_odds:
        home_team = event.get("home_team")
        away_team = event.get("away_team")

        if not home_team or not away_team:
            continue

        print(f"Checking: {home_team} vs {away_team}")

        resolved = resolve_match(
            home_team,
            away_team,
            event.get("sport_title"),
            MODEL_SEASON_NAME,
        )

        print("RESOLVED:", resolved)

        if any(
            resolved[key] is None
            for key in (
                "home_team_id",
                "away_team_id",
                "league_id",
                "season_id",
            )
        ):
            print(
                "Could not resolve database IDs: "
                f"{home_team} vs {away_team}"
            )
            continue

        fixture = {
            "date": event.get("commence_time", ""),
            "league": event.get(
                "sport_title",
                event.get("sport_key", "Unknown"),
            ),
            "home_team": home_team,
            "away_team": away_team,
        }

        try:
            prediction_result = predict_match(
                home_team_id=resolved["home_team_id"],
                away_team_id=resolved["away_team_id"],
                league_id=resolved["league_id"],
                season_id=resolved["season_id"],
            )
            prediction = prediction_to_dict(prediction_result)
        except Exception as error:
            print(
                "Prediction failed for "
                f"{home_team} vs {away_team}: {error}"
            )
            continue

        markets = scan_value_markets(
            event,
            prediction,
            home_team,
            away_team,
        )

        if not markets:
            if include_passes:
                picks.append(
                    build_pass_pick(
                        fixture,
                        prediction,
                    )
                )

            if len(picks) >= limit:
                break

            continue

        best = markets[0]

        if best["is_value"]:
            picks.append(
                build_value_pick(
                    fixture,
                    prediction,
                    best,
                )
            )
        else:
            picks.append(
                build_no_value_pick(
                    fixture,
                    prediction,
                    best,
                )
            )

        if len(picks) >= limit:
            break

    return picks[:limit]