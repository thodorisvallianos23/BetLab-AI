import pandas as pd
import streamlit as st

from dashboard.sidebar import render_analyzer_controls
from models.prediction_engine import fair_odds, predict_match
from models.value_engine import analyze_market


def render_analyzer_page(teams):
    home_team, away_team, selected_market, market_label, bookmakers, predict_button = (
        render_analyzer_controls(teams)
    )

    if not predict_button:
        st.info("Διάλεξε ομάδες και πάτα Predict Match.")
        return

    if home_team == away_team:
        st.error("❌ Home Team και Away Team δεν μπορούν να είναι ίδια ομάδα.")
        return

    prediction = predict_match(home_team, away_team)

    if prediction is None:
        st.error("Could not calculate prediction.")
        return

    st.success(f"Prediction for {home_team} vs {away_team}")

    st.subheader("📌 Match Summary")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Home xG", f"{prediction['home_xg']:.2f}")
    s2.metric("Away xG", f"{prediction['away_xg']:.2f}")
    s3.metric("Total xG", f"{prediction['total_xg']:.2f}")
    s4.metric("AI Rating", "⭐" * prediction["stars"], f"{prediction['stars']}/5")

    st.subheader("🎯 Best Bet Recommendation")
    best_bet = prediction["best_bet"]

    st.success(
        f"Best Bet: {best_bet['market']} | "
        f"Probability: {best_bet['probability'] * 100:.2f}% | "
        f"Fair Odds: {best_bet['fair_odds']:.2f}"
    )

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

    if selected_market == "Match Result":
        model_prob = prediction["home_win"]
    elif selected_market == "BTTS":
        model_prob = prediction["btts"]
    else:
        model_prob = prediction["over_25"]

    value = analyze_market(model_prob, bookmakers)

    v1, v2, v3 = st.columns(3)
    v1.metric("Best Bookmaker", value["best_bookmaker"], f"Odds {value['best_odds']:.2f}")
    v2.metric("Market", market_label)
    v3.metric("Edge", f"{value['edge'] * 100:.2f}%")

    st.write(value["decision"]) 