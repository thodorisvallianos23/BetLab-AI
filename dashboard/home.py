import streamlit as st

from models.todays_picks_engine import get_todays_picks
from services.bankroll_service import get_bankroll
from services.bet_service import get_all_bets
from services.tracker_stats import calculate_tracker_stats


def render_home():
    st.subheader("🏠 Home Dashboard")

    picks = get_todays_picks()
    bankroll = get_bankroll()
    bets = get_all_bets()

    if bankroll:
        starting_balance, current_balance, currency = bankroll
    else:
        starting_balance, current_balance, currency = 1000.0, 1000.0, "EUR"

    stats = calculate_tracker_stats(starting_balance, current_balance, bets)

    c1, c2, c3 = st.columns(3)

    c1.metric("💰 Current Bankroll", f"{currency} {current_balance:.2f}")
    c2.metric("📈 ROI", f"{stats['roi']:.2f}%")
    c3.metric("🏆 Win Rate", f"{stats['win_rate']:.2f}%")

    st.divider()

    st.subheader("⭐ AI Match of the Day")

    if picks:
        best = picks[0]

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Match", best["match"])
        m2.metric("Best Bet", best["market"])
        m3.metric("Confidence", f"{best['confidence']:.1f}%")
        m4.metric("Fair Odds", f"{best['fair_odds']:.2f}")

        st.write("#### Why BetLab likes it")
        for reason in best["explanation"]:
            st.write(reason)
    else:
        st.info("No AI picks found for today.")

    st.divider()

    st.subheader("🔥 Today's Picks")

    if picks:
        for pick in picks:
            with st.container():
                st.write(f"### {pick['match']}")
                st.write(
                    f"**Market:** {pick['market']} | "
                    f"**Probability:** {pick['probability'] * 100:.2f}% | "
                    f"**Confidence:** {pick['confidence']:.1f}% | "
                    f"**Stars:** {'⭐' * pick['stars']}"
                )
                st.divider()
    else:
        st.info("No picks available.")