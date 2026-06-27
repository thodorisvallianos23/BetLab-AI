import math
import sqlite3
from pathlib import Path

import streamlit as st

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


def get_teams():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT team_name
        FROM teams
        ORDER BY team_name
    """)

    teams = [row[0] for row in cursor.fetchall()]
    conn.close()
    return teams


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


def predict_match(home_team, away_team):
    home = get_team_rating(home_team)
    away = get_team_rating(away_team)

    if not home or not away:
        return None

    home_attack, home_defence = home
    away_attack, away_defence = away

    home_xg = max(0.2, (home_attack / 50) * (100 - away_defence) / 50 + 0.35)
    away_xg = max(0.2, (away_attack / 50) * (100 - home_defence) / 50)
    total_xg = home_xg + away_xg

    return {
        "home_xg": home_xg,
        "away_xg": away_xg,
        "total_xg": total_xg,
        "over_15": over_probability(total_xg, 1.5),
        "over_25": over_probability(total_xg, 2.5),
        "over_35": over_probability(total_xg, 3.5),
    }


st.set_page_config(page_title="BetLab AI", layout="wide")

st.title("⚽ BetLab AI Pro")

st.markdown("""
### AI Football Analytics Platform

**Developer:** Thodoris Vallianos

Powered by:
- 📊 Statistical Models
- ⚽ Poisson Goal Engine
- 💰 Value Betting Engine
- 🤖 AI Decision Support
""")

st.divider()

st.caption(
    "BetLab AI Pro v0.1 • © 2026 • Developed by Thodoris Vallianos"
)
teams = get_teams()

col1, col2 = st.columns(2)

with col1:
    home_team = st.selectbox("Home Team", teams)

with col2:
    away_team = st.selectbox("Away Team", teams)

book_odds_o25 = st.number_input(
    "Bookmaker Odds Over 2.5",
    min_value=1.01,
    max_value=20.00,
    value=1.80,
    step=0.01,
)

st.write("---")

if st.button("Predict Match"):
    if home_team == away_team:
        st.error("❌ Home Team και Away Team δεν μπορούν να είναι ίδια ομάδα.")
        st.stop()

    prediction = predict_match(home_team, away_team)

    if prediction is None:
        st.error("Could not calculate prediction.")
        st.stop()

    st.success(f"Prediction for {home_team} vs {away_team}")

    c1, c2, c3 = st.columns(3)

    c1.metric("Home xG", f"{prediction['home_xg']:.2f}")
    c2.metric("Away xG", f"{prediction['away_xg']:.2f}")
    c3.metric("Total xG", f"{prediction['total_xg']:.2f}")

    st.write("### Over Goals Probabilities")

    st.write(
        f"Over 1.5: {prediction['over_15'] * 100:.2f}% "
        f"| Fair Odds: {fair_odds(prediction['over_15']):.2f}"
    )

    st.write(
        f"Over 2.5: {prediction['over_25'] * 100:.2f}% "
        f"| Fair Odds: {fair_odds(prediction['over_25']):.2f}"
    )

    st.write(
        f"Over 3.5: {prediction['over_35'] * 100:.2f}% "
        f"| Fair Odds: {fair_odds(prediction['over_35']):.2f}"
    )

    st.write("### Value Check")

    model_prob = prediction["over_25"]
    implied_prob = 1 / book_odds_o25
    edge = model_prob - implied_prob
    fair_o25 = fair_odds(model_prob)

    v1, v2, v3 = st.columns(3)

    v1.metric("Bookmaker Odds O2.5", f"{book_odds_o25:.2f}")
    v2.metric("Fair Odds O2.5", f"{fair_o25:.2f}")
    v3.metric("Edge", f"{edge * 100:.2f}%")

    if edge >= 0.10:
        st.success("✅ BET - Strong value")
    elif edge >= 0.05:
        st.warning("👀 WATCH - Small value")
    else:
        st.error("❌ PASS - No value")