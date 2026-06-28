import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(".")
from models.prediction_engine import predict_match, fair_odds
from dashboard.sidebar import render_sidebar
DB_PATH = Path("data/betlab_v2.db")


def get_teams():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT team_name FROM teams ORDER BY team_name")
    teams = [row[0] for row in cursor.fetchall()]
    conn.close()
    return teams


st.set_page_config(page_title="BetLab AI Pro", layout="wide")

st.title("⚽ BetLab AI Pro")
st.caption("AI Football Analytics Platform • Prediction Engine v0.2")

teams = get_teams()

home_team, away_team, selected_market, market_label, bookmakers, predict_button = render_sidebar(teams)
if predict_button:
    if home_team == away_team:
        st.error("❌ Home Team και Away Team δεν μπορούν να είναι ίδια ομάδα.")
        st.stop()

    prediction = predict_match(home_team, away_team)

    if prediction is None:
        st.error("Could not calculate prediction.")
        st.stop()

    st.success(f"Prediction for {home_team} vs {away_team}")

    st.subheader("📌 Match Summary")
    st.subheader("🎯 Best Bet Recommendation")

    best_bet = prediction["best_bet"]

    st.success(
        f"Best Bet: {best_bet['market']} | "
        f"Probability: {best_bet['probability'] * 100:.2f}% | "
        f"Fair Odds: {best_bet['fair_odds']:.2f}"
    )
    s1, s2, s3, s4 = st.columns(4)

    s1.metric("Home xG", f"{prediction['home_xg']:.2f}")
    s2.metric("Away xG", f"{prediction['away_xg']:.2f}")
    s3.metric("Total xG", f"{prediction['total_xg']:.2f}")
    s4.metric("AI Rating", "⭐" * prediction["stars"], f"{prediction['stars']}/5")

    st.divider()

    st.subheader("🤖 AI Confidence")

    confidence = prediction["confidence"]

    if confidence >= 80:
        label = "🟢 Elite"
    elif confidence >= 65:
        label = "🟢 High"
    elif confidence >= 50:
        label = "🟡 Medium"
    elif confidence >= 35:
        label = "🟠 Low"
    else:
        label = "🔴 Very Low"

    st.metric("Confidence Score", f"{confidence:.1f}/100", label)

    st.divider()

    st.subheader("📊 Team Context")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Home Form", f"{prediction['home_form']:.1f}")
    c2.metric("Away Form", f"{prediction['away_form']:.1f}")
    c3.metric("Home Strength", f"{prediction['home_strength']:.1f}")
    c4.metric("Away Strength", f"{prediction['away_strength']:.1f}")

    st.divider()

    st.subheader("🏆 Match Outcome Probabilities")

    o1, ox, o2 = st.columns(3)

    o1.metric(
        "Home Win",
        f"{prediction['home_win'] * 100:.2f}%",
        f"Fair {prediction['fair_home_win']:.2f}",
    )

    ox.metric(
        "Draw",
        f"{prediction['draw'] * 100:.2f}%",
        f"Fair {prediction['fair_draw']:.2f}",
    )

    o2.metric(
        "Away Win",
        f"{prediction['away_win'] * 100:.2f}%",
        f"Fair {prediction['fair_away_win']:.2f}",
    )

    outcome_df = pd.DataFrame(
        {
            "Outcome": ["Home Win", "Draw", "Away Win"],
            "Probability": [
                prediction["home_win"] * 100,
                prediction["draw"] * 100,
                prediction["away_win"] * 100,
            ],
        }
    )

    st.bar_chart(outcome_df.set_index("Outcome"))

    st.divider()

    st.subheader("🤝 BTTS")

    b1, b2 = st.columns(2)

    b1.metric("Both Teams To Score", f"{prediction['btts'] * 100:.2f}%")
    b2.metric("Fair Odds BTTS", f"{prediction['fair_btts']:.2f}")

    st.divider()

    st.subheader("🎯 Top 10 Correct Scores")

    score_rows = []

    for score in prediction["correct_scores"]:
        score_rows.append(
            {
                "Score": score["score"],
                "Probability": round(score["probability"] * 100, 2),
                "Fair Odds": round(score["fair_odds"], 2),
            }
        )

    score_df = pd.DataFrame(score_rows)

    st.dataframe(score_df, use_container_width=True)
    st.bar_chart(score_df.set_index("Score")["Probability"])

    st.divider()

    st.subheader("⚽ Over Goals")

    g1, g2, g3 = st.columns(3)

    g1.metric(
        "Over 1.5",
        f"{prediction['over_15'] * 100:.2f}%",
        f"Fair {fair_odds(prediction['over_15']):.2f}",
    )

    g2.metric(
        "Over 2.5",
        f"{prediction['over_25'] * 100:.2f}%",
        f"Fair {fair_odds(prediction['over_25']):.2f}",
    )

    g3.metric(
        "Over 3.5",
        f"{prediction['over_35'] * 100:.2f}%",
        f"Fair {fair_odds(prediction['over_35']):.2f}",
    )

    st.divider()

    st.subheader("💰 Value Check")

    model_prob = prediction["over_25"]
    implied_prob = 1 / book_odds_o25
    edge = model_prob - implied_prob
    fair_o25 = fair_odds(model_prob)

    v1, v2, v3 = st.columns(3)

    v1.metric("Best Bookmaker", best_bookmaker, f"Odds {book_odds_o25:.2f}")
    v2.metric("Fair Odds O2.5", f"{fair_o25:.2f}")
    v3.metric("Edge", f"{edge * 100:.2f}%")

    if edge >= 0.10:
        st.success("✅ BET - Strong value")
    elif edge >= 0.05:
        st.warning("👀 WATCH - Small value")
    else:
        st.error("❌ PASS - No value")

else:
    st.info("Διάλεξε ομάδες από το sidebar και πάτα Predict Match.")

st.divider()
st.caption("BetLab AI Pro v0.2 • © 2026 • Developed by Thodoris Vallianos")