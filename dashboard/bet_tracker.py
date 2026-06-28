import pandas as pd
import streamlit as st

from services.bankroll_service import get_bankroll, set_starting_balance
from services.bet_service import get_all_bets, save_bet, update_bet_result


def render_bet_tracker():
    st.subheader("📒 Bet Tracker")

    bankroll = get_bankroll()

    if bankroll:
        starting_balance, current_balance, currency = bankroll
    else:
        starting_balance, current_balance, currency = 1000.0, 1000.0, "EUR"

    profit = current_balance - starting_balance
    roi = (profit / starting_balance) * 100 if starting_balance > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Current Balance", f"{currency} {current_balance:.2f}")
    c2.metric("📈 Profit/Loss", f"{currency} {profit:.2f}")
    c3.metric("📊 ROI", f"{roi:.2f}%")

    with st.expander("⚙️ Bankroll Settings"):
        new_balance = st.number_input(
            "Starting Balance",
            min_value=0.0,
            value=float(starting_balance),
            step=10.0,
        )

        if st.button("Update Starting Balance"):
            set_starting_balance(new_balance)
            st.success("✅ Balance updated. Refresh the page.")

    st.divider()

    with st.expander("➕ Add Bet", expanded=False):
        with st.form("bet_tracker_form"):
            bet_date = st.date_input("Bet Date")
            match_name = st.text_input("Match")
            market = st.text_input("Market")
            selection = st.selectbox(
           "Selection",
            ["Yes", "No"],
)
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

    st.divider()

    st.subheader("📋 Bet History")

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

        st.subheader("✅ Update Bet Result")

        bet_id = st.number_input(
            "Bet ID",
            min_value=1,
            step=1,
        )

        result = st.selectbox(
            "Result",
            ["Pending", "Won", "Lost", "Push"],
        )

        if st.button("Update Result"):
            selected_bet = df[df["ID"] == bet_id]

            if selected_bet.empty:
                st.error("Bet ID not found.")
            else:
                odds = float(selected_bet.iloc[0]["Odds"])
                stake = float(selected_bet.iloc[0]["Stake"])

                if result == "Won":
                    profit_loss = stake * (odds - 1)
                elif result == "Lost":
                    profit_loss = -stake
                else:
                    profit_loss = 0

                update_bet_result(bet_id, result, profit_loss)
                st.success("✅ Bet result updated. Refresh the page.")
    else:
        st.info("No bets saved yet.")