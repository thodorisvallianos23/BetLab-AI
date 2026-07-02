from services.football_api import get_today_fixtures
from services.odds_api import (
    get_live_odds,
    extract_match_odds,
    extract_totals_odds,
    compare_odds_with_model,
)
from models.prediction_engine import predict_match


TEAM_NAME_MAP = {
    "United States": "USA",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cape Verde",
}


def normalize_team_name(name):
    return TEAM_NAME_MAP.get(name, name)


def explain_pick(prediction):
    reasons = []

    if prediction["confidence"] >= 65:
        reasons.append("✅ Strong AI confidence")

    if prediction["total_xg"] >= 2.7:
        reasons.append("✅ High projected total xG")

    if prediction["home_form"] >= 65:
        reasons.append("✅ Home team is in good form")

    if prediction["btts"] >= 0.55:
        reasons.append("✅ Both teams likely to score")

    if not reasons:
        reasons.append("ℹ️ Moderate model signal")

    return reasons


def find_odds_event(live_odds, home_team, away_team):
    home_team = normalize_team_name(home_team)
    away_team = normalize_team_name(away_team)

    for event in live_odds:
        if event.get("home_team") == home_team and event.get("away_team") == away_team:
            return event

    return None


def get_todays_picks(limit=3):
    fixtures = get_today_fixtures()
    live_odds = get_live_odds()
    picks = []

    for fixture in fixtures:
        home_team = fixture["home_team"]
        away_team = fixture["away_team"]

        prediction = predict_match(home_team, away_team)

        if prediction is None:
            continue

        best_bet = prediction["best_bet"]

        best_bookmaker = "N/A"
        best_odds = 0
        value_percent = 0
        is_value = False

        event = find_odds_event(live_odds, home_team, away_team)

        if event:
            if best_bet["market"] == "Over 2.5":
                odds_rows = extract_totals_odds(event, point=2.5, outcome_name="Over")
                model_prob = prediction["over_25"]

            elif best_bet["market"] == "Over 1.5":
                odds_rows = extract_totals_odds(event, point=2.5, outcome_name="Over")
                model_prob = prediction["over_25"]

            else:
                odds_rows = extract_match_odds(
                    event,
                    normalize_team_name(home_team),
                )
                model_prob = prediction["home_win"]

            value_rows = compare_odds_with_model(model_prob, odds_rows)

            if value_rows:
                best_value = value_rows[0]
                best_bookmaker = best_value["bookmaker"]
                best_odds = best_value["odds"]
                value_percent = best_value["value_percent"]
                is_value = best_value["is_value"]

        picks.append(
            {
                "date": fixture["date"],
                "league": fixture["league"],
                "match": f"{home_team} vs {away_team}",
                "market": best_bet["market"],
                "probability": best_bet["probability"],
                "fair_odds": best_bet["fair_odds"],
                "confidence": prediction["confidence"],
                "stars": prediction["stars"],
                "best_bookmaker": best_bookmaker,
                "best_odds": best_odds,
                "value_percent": value_percent,
                "is_value": is_value,
                "explanation": explain_pick(prediction),
            }
        )

    picks.sort(key=lambda x: (x["is_value"], x["confidence"]), reverse=True)
    return picks[:limit]