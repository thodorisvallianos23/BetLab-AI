import pandas as pd
import streamlit as st

from services.bet_service import get_all_bets, save_bet


def render_bet_tracker():
    st.subheader("📒 Bet Tracker")

    with st.form("bet_tracker_form"):
        bet_date = st.date_input("Bet Date")
        match_name = st.text_input("Match")
        market = st.text_input("Market")
        selection = st.text_input("Selection")
        bookmaker = st.text_input("Bookmaker")
        odds = st.number_input("Odds", min_value=1.01, value=1.80, step=0.01)
        stake = st.number_input("Stake", min_value=0.0, value=10.0, step=1.0)

        submitted = st.form_submit_button("Save Bet")

        if submitted:
            save_bet(
                str(bet_date),
                match_name,
                market,
                selection,
                bookmaker,
                odds,
                stake,
            )
            st.success("✅ Bet saved")

    bets = get_all_bets()

    if bets:
        df = pd.DataFrame(
            bets,
            columns=[
                "ID",
                "Date",
                "Match",
                "Market",
                "Selection",
                "Bookmaker",
                "Odds",
                "Stake",
                "Result",
                "Profit/Loss",
            ],
        )

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No bets saved yet.")