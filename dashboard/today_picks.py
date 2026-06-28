import streamlit as st


def render_today_picks():
    st.subheader("🔥 Today's AI Picks")

    st.markdown("### ⭐ AI Match of the Day")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Match", "Arsenal vs Chelsea")
    col2.metric("Best Bet", "Over 2.5")
    col3.metric("Confidence", "86%")
    col4.metric("Value", "+11.2%")

    st.success("Bet365 offers 1.95 while BetLab fair odds are 1.75.")

    st.divider()

    st.markdown("### 🎯 Today's Top Value Bets")

    picks = [
        {
            "Match": "Arsenal vs Chelsea",
            "Market": "Over 2.5",
            "Bookmaker": "Bet365",
            "Odds": 1.95,
            "Confidence": "86%",
            "Value": "+11.2%",
        },
        {
            "Match": "Liverpool vs Aston Villa",
            "Market": "BTTS Yes",
            "Bookmaker": "Stoiximan",
            "Odds": 1.82,
            "Confidence": "78%",
            "Value": "+7.8%",
        },
    ]

    st.dataframe(picks, use_container_width=True)