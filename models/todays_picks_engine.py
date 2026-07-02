from services.football_api import get_today_fixtures
from models.prediction_engine import predict_match


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


def get_todays_picks(limit=3):
    fixtures = get_today_fixtures()
    picks = []

    for fixture in fixtures:
        prediction = predict_match(
            fixture["home_team"],
            fixture["away_team"],
        )

        if prediction is None:
            continue

        best_bet = prediction["best_bet"]

        picks.append({
            "date": fixture["date"],
            "league": fixture["league"],
            "match": f"{fixture['home_team']} vs {fixture['away_team']}",
            "market": best_bet["market"],
            "probability": best_bet["probability"],
            "fair_odds": best_bet["fair_odds"],
            "confidence": prediction["confidence"],
            "stars": prediction["stars"],
            "explanation": explain_pick(prediction),
        })

    picks.sort(key=lambda x: x["confidence"], reverse=True)
    return picks[:limit]