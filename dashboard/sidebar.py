import streamlit as st


def render_analyzer_controls(teams):
    st.subheader("🔍 Analyzer Setup")

    col1, col2, col3 = st.columns(3)

    with col1:
        home_team = st.selectbox("Home Team", teams)

    with col2:
        away_team = st.selectbox("Away Team", teams)

    with col3:
        selected_market = st.selectbox(
            "Market",
            ["Match Result", "Over Goals", "BTTS"],
        )

    if selected_market == "Match Result":
        market_label = "Home Win"
        odds_title = "Bookmaker Odds - Match Result"
        suffix = "Home"
        default_odds = 2.00

    elif selected_market == "Over Goals":
        market_label = "Over 2.5"
        odds_title = "Bookmaker Odds - Over 2.5"
        suffix = "O2.5"
        default_odds = 1.80

    else:
        market_label = "BTTS Yes"
        odds_title = "Bookmaker Odds - BTTS Yes"
        suffix = "BTTS"
        default_odds = 1.80

    st.write(f"### {odds_title}")

    b1, b2, b3, b4, b5 = st.columns(5)

    bookmakers = {
        "Bet365": b1.number_input(f"Bet365 {suffix}", 1.01, 100.0, default_odds, 0.01),
        "Stoiximan": b2.number_input(f"Stoiximan {suffix}", 1.01, 100.0, default_odds, 0.01),
        "Novibet": b3.number_input(f"Novibet {suffix}", 1.01, 100.0, default_odds, 0.01),
        "Betsson": b4.number_input(f"Betsson {suffix}", 1.01, 100.0, default_odds, 0.01),
        "Fonbet": b5.number_input(f"Fonbet {suffix}", 1.01, 100.0, default_odds, 0.01),
    }

    predict_button = st.button("🔮 Predict Match")

    return home_team, away_team, selected_market, market_label, bookmakers, predict_button