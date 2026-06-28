import streamlit as st


def render_sidebar(teams):
    with st.sidebar:
        st.header("Match Setup")

        home_team = st.selectbox("Home Team", teams)
        away_team = st.selectbox("Away Team", teams)

        st.subheader("Market")

        selected_market = st.selectbox(
            "Select Market",
            ["Match Result", "Over Goals", "BTTS"],
        )

        if selected_market == "Match Result":
            st.subheader("Bookmaker Odds - Match Result")
            market_label = "Home Win"

            bookmakers = {
                "Bet365": st.number_input("Bet365 Home", 1.01, 100.0, 2.00, 0.01),
                "Stoiximan": st.number_input("Stoiximan Home", 1.01, 100.0, 2.00, 0.01),
                "Novibet": st.number_input("Novibet Home", 1.01, 100.0, 2.00, 0.01),
                "Betsson": st.number_input("Betsson Home", 1.01, 100.0, 2.00, 0.01),
                "Fonbet": st.number_input("Fonbet Home", 1.01, 100.0, 2.00, 0.01),
            }

        elif selected_market == "Over Goals":
            st.subheader("Bookmaker Odds - Over 2.5")
            market_label = "Over 2.5"

            bookmakers = {
                "Bet365": st.number_input("Bet365 O2.5", 1.01, 100.0, 1.80, 0.01),
                "Stoiximan": st.number_input("Stoiximan O2.5", 1.01, 100.0, 1.80, 0.01),
                "Novibet": st.number_input("Novibet O2.5", 1.01, 100.0, 1.80, 0.01),
                "Betsson": st.number_input("Betsson O2.5", 1.01, 100.0, 1.80, 0.01),
                "Fonbet": st.number_input("Fonbet O2.5", 1.01, 100.0, 1.80, 0.01),
            }

        else:
            st.subheader("Bookmaker Odds - BTTS Yes")
            market_label = "BTTS Yes"

            bookmakers = {
                "Bet365": st.number_input("Bet365 BTTS", 1.01, 100.0, 1.80, 0.01),
                "Stoiximan": st.number_input("Stoiximan BTTS", 1.01, 100.0, 1.80, 0.01),
                "Novibet": st.number_input("Novibet BTTS", 1.01, 100.0, 1.80, 0.01),
                "Betsson": st.number_input("Betsson BTTS", 1.01, 100.0, 1.80, 0.01),
                "Fonbet": st.number_input("Fonbet BTTS", 1.01, 100.0, 1.80, 0.01),
            }

        predict_button = st.button("🔮 Predict Match")

    return home_team, away_team, selected_market, market_label, bookmakers, predict_button