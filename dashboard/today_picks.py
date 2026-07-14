import pandas as pd
import streamlit as st

from models.todays_picks_engine import get_todays_picks
from services.bet_service import bet_already_exists, save_bet


def get_selection_from_market(market):
    if market.startswith("Over"):
        return "Over"

    if market.startswith("Under"):
        return "Under"

    if market == "Home Win":
        return "Home"

    if market == "Away Win":
        return "Away"

    if market == "Draw":
        return "Draw"

    return market


def render_today_picks():
    st.subheader("🔥 Today's AI Picks")

    picks = get_todays_picks(limit=10)

    if not picks:
        st.info("Δεν βρέθηκαν διαθέσιμα AI picks.")
        return

    match_of_day = picks[0]

    st.markdown("### ⭐ AI Match of the Day")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Match",
        match_of_day["match"],
    )

    col2.metric(
        "Best Bet",
        match_of_day["market"],
    )

    col3.metric(
        "Confidence",
        f"{match_of_day['confidence']:.1f}%",
    )

    col4.metric(
        "Expected Value",
        f"{match_of_day['expected_value_percent']:+.2f}%",
    )

    col5.metric(
        "Suggested Stake",
        f"€{match_of_day['suggested_stake']:.2f}",
    )

    if match_of_day["best_bookmaker"] != "N/A":
        message = (
            f"{match_of_day['best_bookmaker']} offers "
            f"{match_of_day['best_odds']:.2f}, while BetLab fair odds "
            f"are {match_of_day['fair_odds']:.2f}. "
            f"Quarter Kelly: "
            f"{match_of_day['quarter_kelly_percent']:.2f}% of bankroll. "
            f"Suggested stake: €{match_of_day['suggested_stake']:.2f}."
        )

        if match_of_day["is_value"]:
            st.success(f"🟢 VALUE BET FOUND — {message}")
        else:
            st.warning(f"🟡 No strong value — {message}")
    else:
        st.info(
            "Δεν βρέθηκαν διαθέσιμες αποδόσεις για τη συγκεκριμένη αγορά."
        )

    st.markdown("#### Why BetLab likes this pick")

    for reason in match_of_day["explanation"]:
        st.write(reason)

    can_add_to_tracker = (
        match_of_day["best_bookmaker"] != "N/A"
        and match_of_day["best_odds"] > 1
        and match_of_day["suggested_stake"] > 0
    )

    if st.button(
        "➕ Add Match of the Day to Bet Tracker",
        disabled=not can_add_to_tracker,
        use_container_width=True,
    ):
        selection = get_selection_from_market(
            match_of_day["market"]
        )

        try:
            already_exists = bet_already_exists(
                bet_date=match_of_day["date"],
                match_name=match_of_day["match"],
                market=match_of_day["market"],
                bookmaker=match_of_day["best_bookmaker"],
                odds=match_of_day["best_odds"],
            )

            if already_exists:
                st.warning(
                    "⚠️ Αυτό το pick υπάρχει ήδη ως Pending στο Bet Tracker."
                )
            else:
                save_bet(
                    bet_date=match_of_day["date"],
                    match_name=match_of_day["match"],
                    market=match_of_day["market"],
                    selection=selection,
                    bookmaker=match_of_day["best_bookmaker"],
                    odds=match_of_day["best_odds"],
                    stake=match_of_day["suggested_stake"],
                )

                st.success(
                    "✅ Το pick προστέθηκε επιτυχώς στο Bet Tracker."
                )

        except Exception as error:
            st.error(
                f"❌ Δεν αποθηκεύτηκε το pick: {error}"
            )

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
                "Bookmaker": pick["best_bookmaker"],
                "Best Odds": (
                    f"{pick['best_odds']:.2f}"
                    if pick["best_odds"] > 0
                    else "N/A"
                ),
                "Edge": f"{pick['value_percent']:+.2f}%",
                "EV": f"{pick['expected_value_percent']:+.2f}%",
                "Quarter Kelly": (
                    f"{pick['quarter_kelly_percent']:.2f}%"
                ),
                "Suggested Stake": (
                    f"€{pick['suggested_stake']:.2f}"
                ),
                "Confidence": f"{pick['confidence']:.1f}%",
                "Stars": "⭐" * pick["stars"],
                "Value Bet": (
                    "🟢 Yes"
                    if pick["is_value"]
                    else "🔴 No"
                ),
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )