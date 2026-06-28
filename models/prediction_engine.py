import math
import sqlite3
from pathlib import Path

DB_PATH = Path("data/betlab_v2.db")


def poisson_probability(lam, goals):
    return (math.exp(-lam) * lam**goals) / math.factorial(goals)


def over_probability(total_xg, line):
    max_goals = int(line)
    under_or_equal = sum(
        poisson_probability(total_xg, goals)
        for goals in range(max_goals + 1)
    )
    return 1 - under_or_equal


def fair_odds(probability):
    if probability <= 0:
        return 0
    return 1 / probability


def get_team_rating(team_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attack_rating, defence_rating
        FROM teams
        WHERE team_name = ?
    """, (team_name,))

    result = cursor.fetchone()
    conn.close()
    return result


def get_recent_form(team_name, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM teams WHERE team_name = ?", (team_name,))
    team = cursor.fetchone()

    if not team:
        conn.close()
        return 0

    team_id = team[0]

    cursor.execute("""
        SELECT home_team_id, away_team_id, home_goals, away_goals
        FROM matches
        WHERE home_team_id = ? OR away_team_id = ?
        ORDER BY match_date DESC
        LIMIT ?
    """, (team_id, team_id, limit))

    matches = cursor.fetchall()
    conn.close()

    if not matches:
        return 0

    points = 0
    goals_for = 0
    goals_against = 0

    for home_id, away_id, home_goals, away_goals in matches:
        if home_id == team_id:
            gf = home_goals
            ga = away_goals
        else:
            gf = away_goals
            ga = home_goals

        goals_for += gf
        goals_against += ga

        if gf > ga:
            points += 3
        elif gf == ga:
            points += 1

    max_points = len(matches) * 3
    points_score = (points / max_points) * 100
    goal_balance_score = max(0, min(100, 50 + (goals_for - goals_against) * 5))

    form_rating = (points_score * 0.7) + (goal_balance_score * 0.3)

    return round(form_rating, 2)


def predict_match(home_team, away_team):
    home = get_team_rating(home_team)
    away = get_team_rating(away_team)

    if not home or not away:
        return None

    home_attack, home_defence = home
    away_attack, away_defence = away

    home_form = get_recent_form(home_team)
    away_form = get_recent_form(away_team)
    form_boost = (home_form - away_form) / 100

    home_xg = max(
        0.2,
        (home_attack / 50) * (100 - away_defence) / 50 + 0.35 + form_boost
    )

    away_xg = max(
        0.2,
        (away_attack / 50) * (100 - home_defence) / 50 - form_boost
    )

    total_xg = home_xg + away_xg

    return {
        "home_xg": home_xg,
        "away_xg": away_xg,
        "total_xg": total_xg,
        "home_form": home_form,
        "away_form": away_form,
        "over_15": over_probability(total_xg, 1.5),
        "over_25": over_probability(total_xg, 2.5),
        "over_35": over_probability(total_xg, 3.5),
        "fair_o15": fair_odds(over_probability(total_xg, 1.5)),
        "fair_o25": fair_odds(over_probability(total_xg, 2.5)),
        "fair_o35": fair_odds(over_probability(total_xg, 3.5)),
    }