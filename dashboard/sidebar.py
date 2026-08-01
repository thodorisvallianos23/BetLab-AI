import streamlit as st


def render_analyzer_controls(teams, leagues):
    st.subheader("🔍 Analyzer Setup")

    league_col, home_col, away_col, market_col = st.columns(4)

    with league_col:
        selected_league = st.selectbox(
            "League",
            leagues,
        )

    with home_col:
        home_team = st.selectbox(
            "Home Team",
            teams,
        )

    with away_col:
        away_team = st.selectbox(
            "Away Team",
            teams,
        )

    with market_col:
        selected_market = st.selectbox(
            "Market",
            [
                "Match Result",
                "Over Goals",
                "BTTS",
            ],
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
        "Bet365": b1.number_input(
            f"Bet365 {suffix}",
            min_value=1.01,
            max_value=100.0,
            value=default_odds,
            step=0.01,
        ),
        "Stoiximan": b2.number_input(
            f"Stoiximan {suffix}",
            min_value=1.01,
            max_value=100.0,
            value=default_odds,
            step=0.01,
        ),
        "Novibet": b3.number_input(
            f"Novibet {suffix}",
            min_value=1.01,
            max_value=100.0,
            value=default_odds,
            step=0.01,
        ),
        "Betsson": b4.number_input(
            f"Betsson {suffix}",
            min_value=1.01,
            max_value=100.0,
            value=default_odds,
            step=0.01,
        ),
        "Fonbet": b5.number_input(
            f"Fonbet {suffix}",
            min_value=1.01,
            max_value=100.0,
            value=default_odds,
            step=0.01,
        ),
    }

    predict_button = st.button(
        "🔮 Predict Match",
        type="primary",
    )

    return (
        selected_league,
        home_team,
        away_team,
        selected_market,
        market_label,
        bookmakers,
        predict_button,
    )