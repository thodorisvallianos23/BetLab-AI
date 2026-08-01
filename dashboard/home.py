from html import escape
from textwrap import dedent
import streamlit as st

from models.todays_picks_engine import get_todays_picks
from services.bankroll_service import get_bankroll
from services.bet_service import get_all_bets
from services.tracker_stats import calculate_tracker_stats


CURRENCY_SYMBOLS = {
    "EUR": "€",
    "USD": "$",
    "GBP": "£",
}


def safe_text(value):
    return escape(str(value))


def format_currency(value, currency):
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    return f"{symbol}{float(value):,.2f}"


def render_html(html):
    """
    Render HTML without Streamlit treating indentation
    as Markdown code blocks.
    """
    compact_html = "\n".join(
        line.strip()
        for line in dedent(html).splitlines()
        if line.strip()
    )

    st.markdown(
        compact_html,
        unsafe_allow_html=True,
    )


BET_FIELD_INDEX = {
    "id": 0,
    "bet_date": 1,
    "match_name": 2,
    "market": 3,
    "selection": 4,
    "bookmaker": 5,
    "odds": 6,
    "stake": 7,
    "result": 8,
    "status": 8,
    "profit_loss": 9,
}


def get_bet_value(bet, key, default=None):
    """
    Supports dictionaries, sqlite3.Row objects,
    tuples and simple Python objects.
    """
    if bet is None:
        return default

    if isinstance(bet, dict):
        return bet.get(key, default)

    if isinstance(bet, (tuple, list)):
        index = BET_FIELD_INDEX.get(key)

        if index is None or index >= len(bet):
            return default

        value = bet[index]
        return default if value is None else value

    try:
        value = bet[key]
        return default if value is None else value
    except (KeyError, IndexError, TypeError):
        value = getattr(bet, key, default)
        return default if value is None else value


def render_home_styles():
    render_html(
        """
        <style>
            .betlab-home-header {
                margin: 4px 0 24px 0;
            }

            .betlab-eyebrow {
                color: #10B981;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 7px;
            }

            .betlab-home-title {
                color: #111827;
                font-size: 32px;
                line-height: 1.1;
                font-weight: 900;
                letter-spacing: -0.04em;
            }

            .betlab-home-subtitle {
                color: #6B7280;
                font-size: 15px;
                margin-top: 8px;
            }

            .betlab-hero {
                position: relative;
                overflow: hidden;
                border: 1px solid #DDE5E2;
                border-radius: 26px;
                padding: 30px;
                margin-bottom: 20px;
                background:
                    radial-gradient(
                        circle at 85% 35%,
                        rgba(16, 185, 129, 0.22),
                        transparent 28%
                    ),
                    linear-gradient(
                        135deg,
                        #F0FDF9 0%,
                        #FFFFFF 52%,
                        #ECFDF5 100%
                    );
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
            }

            .betlab-hero-badge {
                display: inline-flex;
                align-items: center;
                padding: 7px 12px;
                border: 1px solid #A7F3D0;
                border-radius: 999px;
                background: #ECFDF5;
                color: #047857;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            .betlab-hero-title {
                max-width: 640px;
                margin-top: 18px;
                color: #111827;
                font-size: 38px;
                line-height: 1.05;
                font-weight: 900;
                letter-spacing: -0.045em;
            }

            .betlab-hero-title span {
                color: #10B981;
            }

            .betlab-hero-text {
                max-width: 650px;
                margin-top: 14px;
                color: #4B5563;
                font-size: 16px;
                line-height: 1.65;
            }

            .betlab-section-title {
                color: #111827;
                font-size: 22px;
                font-weight: 900;
                letter-spacing: -0.025em;
                margin: 10px 0 14px 0;
            }

            .betlab-match-card {
                border: 1px solid #DDE5E2;
                border-radius: 24px;
                padding: 24px;
                background:
                    linear-gradient(
                        135deg,
                        rgba(16, 185, 129, 0.10),
                        rgba(255, 255, 255, 0.98) 45%
                    );
                box-shadow: 0 16px 38px rgba(15, 23, 42, 0.07);
                margin-bottom: 14px;
            }

            .betlab-match-top {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 20px;
                flex-wrap: wrap;
            }

            .betlab-match-label {
                color: #047857;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .betlab-match-name {
                margin-top: 8px;
                color: #111827;
                font-size: 25px;
                font-weight: 900;
                letter-spacing: -0.035em;
            }

            .betlab-match-meta {
                margin-top: 7px;
                color: #6B7280;
                font-size: 13px;
            }

            .betlab-market-badge {
                min-width: 160px;
                border: 1px solid #D1FAE5;
                border-radius: 17px;
                padding: 14px 16px;
                background: #FFFFFF;
            }

            .betlab-market-badge-label {
                color: #6B7280;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .betlab-market-badge-value {
                color: #111827;
                font-size: 19px;
                font-weight: 900;
                margin-top: 5px;
            }

            .betlab-match-grid {
                display: grid;
                grid-template-columns:
                    repeat(6, minmax(110px, 1fr));
                gap: 12px;
                margin-top: 22px;
            }

            .betlab-match-stat {
                border: 1px solid #E5E7EB;
                border-radius: 15px;
                padding: 13px;
                background: rgba(255, 255, 255, 0.90);
            }

            .betlab-match-stat-label {
                color: #6B7280;
                font-size: 11px;
                font-weight: 700;
            }

            .betlab-match-stat-value {
                color: #111827;
                font-size: 18px;
                font-weight: 900;
                margin-top: 5px;
            }

            .betlab-pick-row {
                border: 1px solid #E5E7EB;
                border-radius: 17px;
                background: #FFFFFF;
                padding: 15px 17px;
                margin-bottom: 10px;
            }

            .betlab-pick-grid {
                display: grid;
                grid-template-columns:
                    minmax(220px, 2fr)
                    repeat(5, minmax(85px, 1fr));
                gap: 14px;
                align-items: center;
            }

            .betlab-pick-match {
                color: #111827;
                font-size: 15px;
                font-weight: 900;
            }

            .betlab-pick-league {
                color: #6B7280;
                font-size: 12px;
                margin-top: 4px;
            }

            .betlab-pick-label {
                color: #9CA3AF;
                font-size: 10px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .betlab-pick-value {
                color: #111827;
                font-size: 14px;
                font-weight: 900;
                margin-top: 3px;
            }

            .betlab-value-positive {
                color: #059669;
            }

            .betlab-activity-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 14px;
                border-bottom: 1px solid #E5E7EB;
                padding: 13px 0;
            }

            .betlab-activity-item:last-child {
                border-bottom: none;
            }

            .betlab-activity-title {
                color: #111827;
                font-size: 14px;
                font-weight: 800;
            }

            .betlab-activity-meta {
                color: #6B7280;
                font-size: 12px;
                margin-top: 3px;
            }

            .betlab-empty {
                border: 1px dashed #D1D5DB;
                border-radius: 16px;
                padding: 22px;
                color: #6B7280;
                background: #F9FAFB;
                text-align: center;
            }

            @media (max-width: 1100px) {
                .betlab-match-grid {
                    grid-template-columns:
                        repeat(3, minmax(110px, 1fr));
                }

                .betlab-pick-grid {
                    grid-template-columns:
                        repeat(2, minmax(150px, 1fr));
                }
            }

            @media (max-width: 700px) {
                .betlab-hero-title {
                    font-size: 30px;
                }

                .betlab-match-grid {
                    grid-template-columns:
                        repeat(2, minmax(110px, 1fr));
                }

                .betlab-pick-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """
    )


def render_home_header():
    render_html(
        """
        <div class="betlab-home-header">
            <div class="betlab-eyebrow">
                BetLab Intelligence
            </div>

            <div class="betlab-home-title">
                Home Dashboard
            </div>

            <div class="betlab-home-subtitle">
                Your football analytics, bankroll and betting
                performance in one place.
            </div>
        </div>
        """
    )


def render_hero():
    render_html(
        """
        <div class="betlab-hero">
            <div class="betlab-hero-badge">
                ● AI-powered football intelligence
            </div>

            <div class="betlab-hero-title">
                Smarter football analysis.
                <span>Better betting decisions.</span>
            </div>

            <div class="betlab-hero-text">
                BetLab combines calibrated statistical models,
                expected goals, live market prices and disciplined
                bankroll management to identify genuine value.
            </div>
        </div>
        """
    )


def render_summary_metrics(
    picks,
    current_balance,
    currency,
    stats,
):
    value_picks = [
        pick
        for pick in picks
        if pick.get("recommendation_status") == "VALUE"
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Current Bankroll",
        format_currency(
            current_balance,
            currency,
        ),
    )

    col2.metric(
        "💎 Value Bets",
        len(value_picks),
    )

    col3.metric(
        "📈 ROI",
        f"{float(stats.get('roi', 0.0)):.2f}%",
    )

    col4.metric(
        "🏆 Win Rate",
        f"{float(stats.get('win_rate', 0.0)):.2f}%",
    )


def render_match_of_the_day(best):
    match_name = safe_text(best.get("match", "Unknown match"))
    league = safe_text(best.get("league", "Unknown league"))
    match_date = safe_text(best.get("date", ""))
    market = safe_text(best.get("market", "PASS"))

    probability = float(best.get("probability", 0.0)) * 100
    fair_odds = float(best.get("fair_odds", 0.0))
    best_odds = float(best.get("best_odds", 0.0))
    expected_value = float(
        best.get("expected_value_percent", 0.0)
    )
    confidence = float(best.get("confidence", 0.0))
    suggested_stake = float(
        best.get("suggested_stake", 0.0)
    )

    render_html(
        f"""
        <div class="betlab-section-title">
            ⭐ AI Match of the Day
        </div>

        <div class="betlab-match-card">
            <div class="betlab-match-top">
                <div>
                    <div class="betlab-match-label">
                        Featured AI decision
                    </div>

                    <div class="betlab-match-name">
                        {match_name}
                    </div>

                    <div class="betlab-match-meta">
                        {league} · {match_date}
                    </div>
                </div>

                <div class="betlab-market-badge">
                    <div class="betlab-market-badge-label">
                        Recommended market
                    </div>

                    <div class="betlab-market-badge-value">
                        {market}
                    </div>
                </div>
            </div>

            <div class="betlab-match-grid">
                <div class="betlab-match-stat">
                    <div class="betlab-match-stat-label">
                        Probability
                    </div>
                    <div class="betlab-match-stat-value">
                        {probability:.1f}%
                    </div>
                </div>

                <div class="betlab-match-stat">
                    <div class="betlab-match-stat-label">
                        Fair Odds
                    </div>
                    <div class="betlab-match-stat-value">
                        {fair_odds:.2f}
                    </div>
                </div>

                <div class="betlab-match-stat">
                    <div class="betlab-match-stat-label">
                        Best Odds
                    </div>
                    <div class="betlab-match-stat-value">
                        {best_odds:.2f}
                    </div>
                </div>

                <div class="betlab-match-stat">
                    <div class="betlab-match-stat-label">
                        Expected Value
                    </div>
                    <div class="betlab-match-stat-value">
                        {expected_value:+.2f}%
                    </div>
                </div>

                <div class="betlab-match-stat">
                    <div class="betlab-match-stat-label">
                        Confidence
                    </div>
                    <div class="betlab-match-stat-value">
                        {confidence:.1f}%
                    </div>
                </div>

                <div class="betlab-match-stat">
                    <div class="betlab-match-stat-label">
                        Suggested Stake
                    </div>
                    <div class="betlab-match-stat-value">
                        €{suggested_stake:.2f}
                    </div>
                </div>
            </div>
        </div>
        """
    )

    explanations = best.get("explanation", [])

    if explanations:
        with st.expander(
            "Why BetLab reached this decision",
            expanded=False,
        ):
            for reason in explanations:
                st.write(reason)


def render_today_picks_preview(picks, maximum_rows=3):
    render_html(
        """
        <div class="betlab-section-title">
            🔥 Today’s AI Picks
        </div>
        """
    )

    if not picks:
        render_html(
            """
            <div class="betlab-empty">
                No AI picks are currently available.
            </div>
            """
        )
        return

    for pick in picks[:maximum_rows]:
        match_name = safe_text(
            pick.get("match", "Unknown match")
        )
        league = safe_text(
            pick.get("league", "Unknown league")
        )
        market = safe_text(
            pick.get("market", "PASS")
        )
        bookmaker = safe_text(
            pick.get("best_bookmaker", "N/A")
        )

        probability = (
            float(pick.get("probability", 0.0))
            * 100
        )
        best_odds = float(
            pick.get("best_odds", 0.0)
        )
        expected_value = float(
            pick.get("expected_value_percent", 0.0)
        )
        confidence = float(
            pick.get("confidence", 0.0)
        )

        render_html(
            f"""
            <div class="betlab-pick-row">
                <div class="betlab-pick-grid">
                    <div>
                        <div class="betlab-pick-match">
                            {match_name}
                        </div>

                        <div class="betlab-pick-league">
                            {league}
                        </div>
                    </div>

                    <div>
                        <div class="betlab-pick-label">
                            Market
                        </div>
                        <div class="betlab-pick-value">
                            {market}
                        </div>
                    </div>

                    <div>
                        <div class="betlab-pick-label">
                            Probability
                        </div>
                        <div class="betlab-pick-value">
                            {probability:.1f}%
                        </div>
                    </div>

                    <div>
                        <div class="betlab-pick-label">
                            Best Odds
                        </div>
                        <div class="betlab-pick-value">
                            {best_odds:.2f}
                        </div>
                    </div>

                    <div>
                        <div class="betlab-pick-label">
                            EV
                        </div>
                        <div class="
                            betlab-pick-value
                            betlab-value-positive
                        ">
                            {expected_value:+.2f}%
                        </div>
                    </div>

                    <div>
                        <div class="betlab-pick-label">
                            Bookmaker
                        </div>
                        <div class="betlab-pick-value">
                            {bookmaker}
                        </div>
                    </div>

                    <div>
                        <div class="betlab-pick-label">
                            Confidence
                        </div>
                        <div class="betlab-pick-value">
                            {confidence:.1f}%
                        </div>
                    </div>
                </div>
            </div>
            """
        )


def render_recent_activity(bets, maximum_rows=4):
    render_html(
        """
        <div class="betlab-section-title">
            📒 Recent Bet Activity
        </div>
        """
    )

    if not bets:
        render_html(
            """
            <div class="betlab-empty">
                No tracked bets yet.
            </div>
            """
        )
        return

    recent_bets = list(bets)[-maximum_rows:]
    recent_bets.reverse()

    for bet in recent_bets:
        match_name = safe_text(
            get_bet_value(
                bet,
                "match_name",
                "Unknown match",
            )
        )
        market = safe_text(
            get_bet_value(
                bet,
                "market",
                "Unknown market",
            )
        )
        status = safe_text(
            get_bet_value(
                bet,
                "status",
                "Pending",
            )
        )
        bookmaker = safe_text(
            get_bet_value(
                bet,
                "bookmaker",
                "N/A",
            )
        )
        odds = float(
            get_bet_value(
                bet,
                "odds",
                0.0,
            )
            or 0.0
        )

        render_html(
            f"""
            <div class="betlab-activity-item">
                <div>
                    <div class="betlab-activity-title">
                        {match_name} — {market}
                    </div>

                    <div class="betlab-activity-meta">
                        {bookmaker} · Odds {odds:.2f}
                    </div>
                </div>

                <div class="betlab-pick-value">
                    {status}
                </div>
            </div>
            """
        )


def render_home():
    render_home_styles()
    render_home_header()
    render_hero()

    try:
        picks = get_todays_picks(
            limit=10,
            include_passes=True,
        )
    except Exception as error:
        picks = []
        st.error(
            f"Could not load today's AI picks: {error}"
        )

    try:
        bankroll = get_bankroll()
    except Exception as error:
        bankroll = None
        st.warning(
            f"Could not load bankroll data: {error}"
        )

    try:
        bets = get_all_bets()
    except Exception as error:
        bets = []
        st.warning(
            f"Could not load bet tracker data: {error}"
        )

    if bankroll:
        (
            starting_balance,
            current_balance,
            currency,
        ) = bankroll
    else:
        starting_balance = 100.0
        current_balance = 100.0
        currency = "EUR"

    try:
        stats = calculate_tracker_stats(
            starting_balance,
            current_balance,
            bets,
        )
    except Exception:
        stats = {
            "roi": 0.0,
            "win_rate": 0.0,
        }

    render_summary_metrics(
        picks=picks,
        current_balance=current_balance,
        currency=currency,
        stats=stats,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if picks:
        value_picks = [
            pick
            for pick in picks
            if pick.get("recommendation_status") == "VALUE"
        ]

        if value_picks:
            best_pick = value_picks[0]
        else:
            best_pick = picks[0]

        render_match_of_the_day(best_pick)
    else:
        render_html(
            """
            <div class="betlab-section-title">
                ⭐ AI Match of the Day
            </div>

            <div class="betlab-empty">
                No match currently meets the model requirements.
            </div>
            """
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    left_column, right_column = st.columns(
        [1.65, 1],
        gap="large",
    )

    with left_column:
        render_today_picks_preview(
            picks=picks,
            maximum_rows=3,
        )

    with right_column:
        render_recent_activity(
            bets=bets,
            maximum_rows=4,
        )