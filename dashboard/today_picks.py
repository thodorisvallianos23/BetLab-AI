from html import escape
from textwrap import dedent

import pandas as pd
import streamlit as st

from models.todays_picks_engine import get_todays_picks
from services.bet_service import bet_already_exists, save_bet


STATUS_LABELS = {
    "VALUE": "🟢 Value Bet",
    "NO_VALUE": "🟡 No Value",
    "PASS": "⚪ Pass",
}


STATUS_STYLES = {
    "VALUE": {
        "label": "VALUE BET",
        "background": "#DCFCE7",
        "color": "#15803D",
        "border": "#86EFAC",
    },
    "NO_VALUE": {
        "label": "NO VALUE",
        "background": "#FEF3C7",
        "color": "#B45309",
        "border": "#FCD34D",
    },
    "PASS": {
        "label": "PASS / NO BET",
        "background": "#F3F4F6",
        "color": "#4B5563",
        "border": "#D1D5DB",
    },
}



def render_html(html):
    """Render HTML without Markdown treating indentation as code blocks."""
    compact_html = "\n".join(
        line.strip()
        for line in dedent(html).splitlines()
        if line.strip()
    )
    st.markdown(
        compact_html,
        unsafe_allow_html=True,
    )


def safe_text(value):
    return escape(str(value))


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


def render_page_header():
    header_html = dedent("""
<div style="
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:20px;
    margin:4px 0 26px 0;
">
    <div>
        <div style="
            font-size:13px;
            font-weight:800;
            color:#10B981;
            letter-spacing:0.12em;
            text-transform:uppercase;
            margin-bottom:6px;
        ">
            BetLab Intelligence
        </div>

        <div style="
            font-size:34px;
            line-height:1.1;
            font-weight:900;
            color:#111827;
            letter-spacing:-0.04em;
        ">
            Today's AI Picks
        </div>

        <div style="
            margin-top:8px;
            font-size:15px;
            color:#6B7280;
        ">
            Live odds, expected value and risk-adjusted staking.
        </div>
    </div>

    <div style="
        padding:10px 15px;
        background:#ECFDF5;
        color:#047857;
        border:1px solid #A7F3D0;
        border-radius:999px;
        font-size:13px;
        font-weight:800;
        white-space:nowrap;
    ">
        ● Live market scan
    </div>
    </div>
    """)

    render_html(header_html)


def render_featured_card(pick):
    status = pick["recommendation_status"]
    style = STATUS_STYLES.get(status, STATUS_STYLES["PASS"])

    match_name = safe_text(pick["match"])
    league = safe_text(pick.get("league", ""))
    match_date = safe_text(pick.get("date", ""))
    market = safe_text(pick["market"])
    bookmaker = safe_text(pick["best_bookmaker"])

    if status == "PASS":
        probability = "—"
        fair_odds = "—"
        best_odds = "—"
        expected_value = "—"
        stake = "€0.00"
    else:
        probability = f"{pick['probability'] * 100:.1f}%"
        fair_odds = f"{pick['fair_odds']:.2f}"
        best_odds = (
            f"{pick['best_odds']:.2f}"
            if pick["best_odds"] > 0
            else "—"
        )
        expected_value = f"{pick['expected_value_percent']:+.2f}%"
        stake = f"€{pick['suggested_stake']:.2f}"

    card_html = dedent(f"""
    <div style="
        background:
            linear-gradient(
                135deg,
                rgba(16,185,129,0.10),
                rgba(255,255,255,0.95) 42%
            );
        border:1px solid #DDE5E2;
        border-radius:26px;
        padding:28px;
        box-shadow:0 18px 45px rgba(15,23,42,0.08);
        margin-bottom:18px;
    ">
        <div style="
            display:flex;
            align-items:flex-start;
            justify-content:space-between;
            gap:20px;
            flex-wrap:wrap;
        ">
            <div>
                <div style="
                    display:inline-flex;
                    align-items:center;
                    padding:7px 12px;
                    border-radius:999px;
                    background:{style['background']};
                    color:{style['color']};
                    border:1px solid {style['border']};
                    font-size:12px;
                    font-weight:900;
                    letter-spacing:0.06em;
                    margin-bottom:14px;
                ">
                    {style['label']}
                </div>

                <div style="
                    font-size:28px;
                    font-weight:900;
                    color:#111827;
                    letter-spacing:-0.035em;
                    line-height:1.15;
                ">
                    {match_name}
                </div>

                <div style="
                    margin-top:8px;
                    color:#6B7280;
                    font-size:14px;
                ">
                    {league} · {match_date}
                </div>
            </div>

            <div style="
                min-width:190px;
                background:#FFFFFF;
                border:1px solid #E5E7EB;
                border-radius:18px;
                padding:16px 18px;
            ">
                <div style="
                    color:#6B7280;
                    font-size:12px;
                    font-weight:700;
                    text-transform:uppercase;
                    letter-spacing:0.08em;
                ">
                    Recommended Market
                </div>

                <div style="
                    margin-top:5px;
                    color:#111827;
                    font-size:21px;
                    font-weight:900;
                ">
                    {market}
                </div>
            </div>
        </div>

        <div style="
            display:grid;
            grid-template-columns:repeat(6, minmax(120px, 1fr));
            gap:12px;
            margin-top:24px;
        ">
            <div class="betlab-stat-card">
                <div class="betlab-stat-label">Probability</div>
                <div class="betlab-stat-value">{probability}</div>
            </div>

            <div class="betlab-stat-card">
                <div class="betlab-stat-label">Fair Odds</div>
                <div class="betlab-stat-value">{fair_odds}</div>
            </div>

            <div class="betlab-stat-card">
                <div class="betlab-stat-label">Best Odds</div>
                <div class="betlab-stat-value">{best_odds}</div>
            </div>

            <div class="betlab-stat-card">
                <div class="betlab-stat-label">Expected Value</div>
                <div class="betlab-stat-value">{expected_value}</div>
            </div>

            <div class="betlab-stat-card">
                <div class="betlab-stat-label">Confidence</div>
                <div class="betlab-stat-value">
                    {pick['confidence']:.1f}%
                </div>
            </div>

            <div class="betlab-stat-card">
                <div class="betlab-stat-label">Suggested Stake</div>
                <div class="betlab-stat-value">{stake}</div>
            </div>
        </div>

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:16px;
            flex-wrap:wrap;
            margin-top:18px;
            padding-top:18px;
            border-top:1px solid #E5E7EB;
        ">
            <div>
                <span style="
                    color:#6B7280;
                    font-size:13px;
                    font-weight:700;
                ">
                    Best bookmaker:
                </span>

                <span style="
                    margin-left:6px;
                    color:#111827;
                    font-size:14px;
                    font-weight:900;
                ">
                    {bookmaker}
                </span>
            </div>

            <div style="
                color:#6B7280;
                font-size:13px;
                font-weight:700;
            ">
                Risk model: Quarter Kelly · Stake cap enabled
            </div>
        </div>
    </div>
    """)

    render_html(card_html)


def render_pick_explanation(pick):
    render_html(
        """
        <div style="
            font-size:17px;
            font-weight:900;
            color:#111827;
            margin:20px 0 10px 0;
        ">
            Why BetLab reached this decision
        </div>
        """
    )

    for reason in pick["explanation"]:
        render_html(
            f"""
            <div style="
                background:#FFFFFF;
                border:1px solid #E5E7EB;
                border-radius:13px;
                padding:11px 14px;
                margin-bottom:8px;
                color:#374151;
                font-size:14px;
                font-weight:600;
            ">
                {safe_text(reason)}
            </div>
            """
        )


def render_market_message(pick):
    status = pick["recommendation_status"]

    if status == "PASS":
        st.warning(
            "Το μοντέλο ανέλυσε τον αγώνα, αλλά δεν βρήκε "
            "market που να πληροί τα όρια αξιοπιστίας."
        )
        return

    if not pick["odds_available"]:
        st.info(
            "Υπάρχει model signal, αλλά δεν βρέθηκαν διαθέσιμες "
            "live αποδόσεις για το συγκεκριμένο market."
        )
        return

    message = (
        f"{pick['best_bookmaker']} προσφέρει απόδοση "
        f"{pick['best_odds']:.2f}, ενώ η fair απόδοση του BetLab "
        f"είναι {pick['fair_odds']:.2f}. "
        f"Edge {pick['value_percent']:+.2f}% και "
        f"Quarter Kelly {pick['quarter_kelly_percent']:.2f}%."
    )

    if status == "VALUE":
        st.success(f"💎 Value detected — {message}")
    else:
        st.warning(f"Δεν υπάρχει αρκετό value — {message}")


def render_add_to_tracker_button(pick):
    status = pick["recommendation_status"]

    can_add_to_tracker = (
        status == "VALUE"
        and pick["best_bookmaker"] != "N/A"
        and pick["best_odds"] > 1
        and pick["suggested_stake"] > 0
    )

    if st.button(
        "➕ Add pick to Bet Tracker",
        disabled=not can_add_to_tracker,
        use_container_width=True,
        type="primary",
    ):
        selection = get_selection_from_market(
            pick["market"]
        )

        try:
            already_exists = bet_already_exists(
                bet_date=pick["date"],
                match_name=pick["match"],
                market=pick["market"],
                bookmaker=pick["best_bookmaker"],
                odds=pick["best_odds"],
            )

            if already_exists:
                st.warning(
                    "Αυτό το pick υπάρχει ήδη ως Pending "
                    "στο Bet Tracker."
                )
            else:
                save_bet(
                    bet_date=pick["date"],
                    match_name=pick["match"],
                    market=pick["market"],
                    selection=selection,
                    bookmaker=pick["best_bookmaker"],
                    odds=pick["best_odds"],
                    stake=pick["suggested_stake"],
                )

                st.success(
                    "Το pick προστέθηκε επιτυχώς στο Bet Tracker."
                )

        except Exception as error:
            st.error(
                f"Δεν αποθηκεύτηκε το pick: {error}"
            )


def render_summary_cards(
    value_picks,
    no_value_picks,
    pass_picks,
):
    total_decisions = (
        len(value_picks)
        + len(no_value_picks)
        + len(pass_picks)
    )

    value_rate = (
        len(value_picks) / total_decisions * 100
        if total_decisions
        else 0.0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💎 Value Bets",
        len(value_picks),
    )

    col2.metric(
        "🟡 No Value",
        len(no_value_picks),
    )

    col3.metric(
        "🛡️ Pass",
        len(pass_picks),
    )

    col4.metric(
        "Value Rate",
        f"{value_rate:.0f}%",
    )


def build_table_rows(picks):
    rows = []

    for pick in picks:
        status = pick["recommendation_status"]

        rows.append(
            {
                "Match": pick["match"],
                "Status": STATUS_LABELS.get(
                    status,
                    status,
                ),
                "Market": pick["market"],
                "Probability": (
                    f"{pick['probability'] * 100:.2f}%"
                    if pick["probability"] > 0
                    else "—"
                ),
                "Fair Odds": (
                    f"{pick['fair_odds']:.2f}"
                    if pick["fair_odds"] > 0
                    else "—"
                ),
                "Bookmaker": (
                    pick["best_bookmaker"]
                    if pick["best_bookmaker"] != "N/A"
                    else "—"
                ),
                "Best Odds": (
                    f"{pick['best_odds']:.2f}"
                    if pick["best_odds"] > 0
                    else "—"
                ),
                "Edge": (
                    f"{pick['value_percent']:+.2f}%"
                    if status != "PASS"
                    else "—"
                ),
                "EV": (
                    f"{pick['expected_value_percent']:+.2f}%"
                    if status != "PASS"
                    else "—"
                ),
                "Stake": (
                    f"€{pick['suggested_stake']:.2f}"
                    if status == "VALUE"
                    else "—"
                ),
                "Confidence": (
                    f"{pick['confidence']:.1f}%"
                ),
                "Rating": "⭐" * pick["stars"],
            }
        )

    return rows


def render_decisions_table(picks):
    render_html(
        """
        <div style="
            margin:4px 0 14px 0;
        ">
            <div style="
                font-size:22px;
                font-weight:900;
                color:#111827;
                letter-spacing:-0.025em;
            ">
                Market Scan Results
            </div>
            <div style="
                color:#6B7280;
                font-size:14px;
                margin-top:4px;
            ">
                Best market found for every available fixture.
            </div>
        </div>
        """
    )

    rows = build_table_rows(picks)
    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Match": st.column_config.TextColumn(
                "Match",
                width="large",
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="medium",
            ),
            "Market": st.column_config.TextColumn(
                "Market",
                width="medium",
            ),
        },
    )


def render_pass_matches(pass_picks):
    if not pass_picks:
        return

    with st.expander(
        f"🛡️ Pass / No Bet matches ({len(pass_picks)})"
    ):
        for pick in pass_picks:
            render_html(
                f"""
                <div style="
                    border:1px solid #E5E7EB;
                    border-radius:15px;
                    padding:14px 16px;
                    margin-bottom:10px;
                    background:#FFFFFF;
                ">
                    <div style="
                        font-size:15px;
                        font-weight:900;
                        color:#111827;
                    ">
                        {safe_text(pick['match'])}
                    </div>

                    <div style="
                        font-size:13px;
                        color:#6B7280;
                        margin-top:4px;
                    ">
                        Confidence: {pick['confidence']:.1f}%
                    </div>
                </div>
                """
            )


def render_today_picks():
    render_page_header()

    picks = get_todays_picks(
        limit=10,
        include_passes=True,
    )

    if not picks:
        st.info(
            "Δεν βρέθηκαν διαθέσιμοι αγώνες για ανάλυση."
        )
        return

    value_picks = [
        pick
        for pick in picks
        if pick["recommendation_status"] == "VALUE"
    ]

    no_value_picks = [
        pick
        for pick in picks
        if pick["recommendation_status"] == "NO_VALUE"
    ]

    pass_picks = [
        pick
        for pick in picks
        if pick["recommendation_status"] == "PASS"
    ]

    if value_picks:
        featured_pick = value_picks[0]
    elif no_value_picks:
        featured_pick = no_value_picks[0]
    else:
        featured_pick = pass_picks[0]

    render_featured_card(featured_pick)
    render_market_message(featured_pick)
    render_pick_explanation(featured_pick)
    render_add_to_tracker_button(featured_pick)

    render_html("<div style='height:18px'></div>")

    render_summary_cards(
        value_picks,
        no_value_picks,
        pass_picks,
    )

    render_html("<div style='height:22px'></div>")

    render_decisions_table(picks)
    render_pass_matches(pass_picks)