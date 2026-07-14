import math
import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def poisson_probability(lam, goals):
    if lam < 0 or goals < 0:
        return 0.0

    return (
        math.exp(-lam)
        * (lam**goals)
        / math.factorial(goals)
    )


def over_probability(total_xg, line):
    """
    Over 1.5 = 2 or more goals.
    Over 2.5 = 3 or more goals.
    Over 3.5 = 4 or more goals.
    """
    if total_xg <= 0:
        return 0.0

    goal_limit = math.floor(line)

    under_probability = sum(
        poisson_probability(total_xg, goals)
        for goals in range(goal_limit + 1)
    )

    probability = 1 - under_probability

    return max(0.0, min(1.0, probability))


def fair_odds(probability):
    if probability <= 0:
        return 0.0

    return 1 / probability


def confidence_score(prediction):
    over_25 = prediction["over_25"]
    total_xg = prediction["total_xg"]
    btts = prediction["btts"]

    score = 0.0

    score += min(total_xg * 20, 40)
    score += over_25 * 35
    score += btts * 15

    return round(min(score, 100), 1)


def star_rating(confidence):
    if confidence >= 80:
        return 5

    if confidence >= 65:
        return 4

    if confidence >= 50:
        return 3

    if confidence >= 35:
        return 2

    return 1


def best_bet_recommendation(prediction):
    """
    Επιλέγει το καλύτερο betting market με βάση:

    1. Minimum probability threshold
    2. Πόσο ξεπερνάει το market το threshold
    3. Market weight
    4. Extra προστασία από οριακά signals

    Αν κανένα market δεν είναι αρκετά δυνατό,
    επιστρέφει No Bet.
    """

    markets = [
        {
            "market": "Home Win",
            "probability": prediction["home_win"],
            "fair_odds": prediction["fair_home_win"],
            "minimum_probability": 0.46,
            "weight": 1.00,
        },
        {
            "market": "Away Win",
            "probability": prediction["away_win"],
            "fair_odds": prediction["fair_away_win"],
            "minimum_probability": 0.46,
            "weight": 1.00,
        },
        {
            "market": "Over 1.5",
            "probability": prediction["over_15"],
            "fair_odds": prediction["fair_o15"],
            "minimum_probability": 0.68,
            "weight": 0.80,
        },
        {
            "market": "Over 2.5",
            "probability": prediction["over_25"],
            "fair_odds": prediction["fair_o25"],
            "minimum_probability": 0.50,
            "weight": 1.25,
        },
        {
            "market": "Over 3.5",
            "probability": prediction["over_35"],
            "fair_odds": prediction["fair_o35"],
            "minimum_probability": 0.34,
            "weight": 1.10,
        },
    ]

    qualified_markets = []

    for market in markets:
        probability = market["probability"]
        minimum_probability = market["minimum_probability"]
        weight = market["weight"]

        probability_edge = (
            probability - minimum_probability
        )

        if probability_edge < 0:
            continue

        signal_score = (
            probability_edge * weight
        )

        market["probability_edge"] = probability_edge
        market["signal_score"] = signal_score

        qualified_markets.append(market)

    if not qualified_markets:
        return {
            "market": "No Bet",
            "probability": 0.0,
            "fair_odds": 0.0,
            "signal_score": 0.0,
            "probability_edge": 0.0,
        }

    qualified_markets.sort(
        key=lambda item: (
            item["signal_score"],
            item["probability"],
        ),
        reverse=True,
    )

    best_market = qualified_markets[0]

    return {
        "market": best_market["market"],
        "probability": best_market["probability"],
        "fair_odds": best_market["fair_odds"],
        "signal_score": best_market["signal_score"],
        "probability_edge": best_market["probability_edge"],
    }


def match_outcome_probabilities(
    home_xg,
    away_xg,
    max_goals=8,
):
    home_win = 0.0
    draw = 0.0
    away_win = 0.0

    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            probability = (
                poisson_probability(home_xg, home_goals)
                * poisson_probability(away_xg, away_goals)
            )

            if home_goals > away_goals:
                home_win += probability
            elif home_goals == away_goals:
                draw += probability
            else:
                away_win += probability

    total_probability = home_win + draw + away_win

    if total_probability > 0:
        home_win /= total_probability
        draw /= total_probability
        away_win /= total_probability

    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
    }


def btts_probability(home_xg, away_xg):
    home_no_goal = poisson_probability(home_xg, 0)
    away_no_goal = poisson_probability(away_xg, 0)
    both_no_goal = home_no_goal * away_no_goal

    probability = (
        1
        - home_no_goal
        - away_no_goal
        + both_no_goal
    )

    return max(0.0, min(1.0, probability))


def correct_score_matrix(
    home_xg,
    away_xg,
    max_goals=6,
):
    scores = []

    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            probability = (
                poisson_probability(home_xg, home_goals)
                * poisson_probability(away_xg, away_goals)
            )

            scores.append(
                {
                    "score": f"{home_goals}-{away_goals}",
                    "probability": probability,
                    "fair_odds": fair_odds(probability),
                }
            )

    scores.sort(
        key=lambda item: item["probability"],
        reverse=True,
    )

    return scores


def get_team_rating(team_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT attack_rating, defence_rating
        FROM teams
        WHERE team_name = ?
        """,
        (team_name,),
    )

    result = cursor.fetchone()
    conn.close()

    return result


def get_recent_form(team_name, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM teams
        WHERE team_name = ?
        """,
        (team_name,),
    )

    team = cursor.fetchone()

    if not team:
        conn.close()
        return 50.0

    team_id = team[0]

    cursor.execute(
        """
        SELECT
            home_team_id,
            away_team_id,
            home_goals,
            away_goals
        FROM matches
        WHERE home_team_id = ?
           OR away_team_id = ?
        ORDER BY match_date DESC
        LIMIT ?
        """,
        (
            team_id,
            team_id,
            limit,
        ),
    )

    matches = cursor.fetchall()
    conn.close()

    if not matches:
        return 50.0

    points = 0
    goals_for = 0
    goals_against = 0

    for (
        home_id,
        away_id,
        home_goals,
        away_goals,
    ) in matches:
        if home_goals is None or away_goals is None:
            continue

        if home_id == team_id:
            goals_scored = home_goals
            goals_conceded = away_goals
        else:
            goals_scored = away_goals
            goals_conceded = home_goals

        goals_for += goals_scored
        goals_against += goals_conceded

        if goals_scored > goals_conceded:
            points += 3
        elif goals_scored == goals_conceded:
            points += 1

    maximum_points = len(matches) * 3

    if maximum_points <= 0:
        return 50.0

    points_score = (
        points / maximum_points
    ) * 100

    goal_balance_score = max(
        0,
        min(
            100,
            50 + (
                goals_for - goals_against
            ) * 5,
        ),
    )

    form_rating = (
        points_score * 0.7
        + goal_balance_score * 0.3
    )

    return round(form_rating, 2)


def get_home_away_strength(team_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM teams
        WHERE team_name = ?
        """,
        (team_name,),
    )

    team = cursor.fetchone()

    if not team:
        conn.close()

        return {
            "home_strength": 50.0,
            "away_strength": 50.0,
        }

    team_id = team[0]

    cursor.execute(
        """
        SELECT
            AVG(home_goals),
            AVG(away_goals)
        FROM matches
        WHERE home_team_id = ?
        """,
        (team_id,),
    )

    home_result = cursor.fetchone()
    home_goals_for = home_result[0] or 0
    home_goals_against = home_result[1] or 0

    cursor.execute(
        """
        SELECT
            AVG(away_goals),
            AVG(home_goals)
        FROM matches
        WHERE away_team_id = ?
        """,
        (team_id,),
    )

    away_result = cursor.fetchone()
    away_goals_for = away_result[0] or 0
    away_goals_against = away_result[1] or 0

    conn.close()

    home_strength = (
        home_goals_for * 30
        + 100
        - home_goals_against * 25
    )

    away_strength = (
        away_goals_for * 30
        + 100
        - away_goals_against * 25
    )

    return {
        "home_strength": round(
            max(0, min(100, home_strength)),
            2,
        ),
        "away_strength": round(
            max(0, min(100, away_strength)),
            2,
        ),
    }


def predict_match(home_team, away_team):
    home_rating = get_team_rating(home_team)
    away_rating = get_team_rating(away_team)

    if not home_rating or not away_rating:
        return None

    home_attack, home_defence = home_rating
    away_attack, away_defence = away_rating

    home_form = get_recent_form(home_team)
    away_form = get_recent_form(away_team)

    form_boost = (
        home_form - away_form
    ) / 100

    home_strength_data = get_home_away_strength(
        home_team
    )

    away_strength_data = get_home_away_strength(
        away_team
    )

    home_strength = home_strength_data[
        "home_strength"
    ]

    away_strength = away_strength_data[
        "away_strength"
    ]

    strength_boost = (
        home_strength - away_strength
    ) / 200

    home_xg = max(
        0.35,
        (
            (home_attack / 55)
            * ((115 - away_defence) / 45)
            + 0.55
            + (form_boost * 0.35)
            + (strength_boost * 0.30)
        ),
    )

    away_xg = max(
        0.30,
        (
            (away_attack / 58)
            * ((112 - home_defence) / 48)
            + 0.30
            - (form_boost * 0.25)
            - (strength_boost * 0.20)
        ),
    )

    total_xg = home_xg + away_xg

    outcome_probs = match_outcome_probabilities(
        home_xg,
        away_xg,
    )

    btts = btts_probability(
        home_xg,
        away_xg,
    )

    over_15 = over_probability(
        total_xg,
        1.5,
    )

    over_25 = over_probability(
        total_xg,
        2.5,
    )

    over_35 = over_probability(
        total_xg,
        3.5,
    )

    scores = correct_score_matrix(
        home_xg,
        away_xg,
    )

    prediction_data = {
        "home_xg": home_xg,
        "away_xg": away_xg,
        "total_xg": total_xg,
        "home_form": home_form,
        "away_form": away_form,
        "home_strength": home_strength,
        "away_strength": away_strength,
        "home_win": outcome_probs["home_win"],
        "draw": outcome_probs["draw"],
        "away_win": outcome_probs["away_win"],
        "fair_home_win": fair_odds(
            outcome_probs["home_win"]
        ),
        "fair_draw": fair_odds(
            outcome_probs["draw"]
        ),
        "fair_away_win": fair_odds(
            outcome_probs["away_win"]
        ),
        "btts": btts,
        "fair_btts": fair_odds(btts),
        "over_15": over_15,
        "over_25": over_25,
        "over_35": over_35,
        "fair_o15": fair_odds(over_15),
        "fair_o25": fair_odds(over_25),
        "fair_o35": fair_odds(over_35),
    }

    confidence = confidence_score(
        prediction_data
    )

    prediction_data["confidence"] = confidence
    prediction_data["stars"] = star_rating(
        confidence
    )

    prediction_data["correct_scores"] = scores[:10]

    prediction_data["best_bet"] = (
        best_bet_recommendation(
            prediction_data
        )
    )

    return prediction_data