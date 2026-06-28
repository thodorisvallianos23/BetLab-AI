import streamlit as st

from models.todays_picks_engine import get_todays_picks


def render_today_picks():
    st.subheader("🔥 Today's AI Picks")

    picks = get_todays_picks()

    if not picks:
        st.info("No AI picks found for today.")
        return

    match_of_day = picks[0]

    st.markdown("### ⭐ AI Match of the Day")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Match", match_of_day["match"])
    col2.metric("Best Bet", match_of_day["market"])
    col3.metric("Confidence", f"{match_of_day['confidence']:.1f}%")
    col4.metric("Fair Odds", f"{match_of_day['fair_odds']:.2f}")

    st.write("#### Why BetLab likes this pick")

    for reason in match_of_day["explanation"]:
        st.write(reason)

    st.divider()

    st.markdown("### 🎯 Today's Top Value Bets")

    rows = []

    for pick in picks:
        rows.append(
            {
                "Match": pick["match"],
                "Market": pick["market"],
                "Probability": f"{pick['probability'] * 100:.2f}%",
                "Fair Odds": f"{pick['fair_odds']:.2f}",
                "Confidence": f"{pick['confidence']:.1f}%",
                "Stars": "⭐" * pick["stars"],
            }
        )

    st.dataframe(rows, use_container_width=True)