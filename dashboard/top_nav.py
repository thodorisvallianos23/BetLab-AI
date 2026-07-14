from textwrap import dedent

import streamlit.components.v1 as components

from services.bankroll_service import get_bankroll


def render_top_nav():
    bankroll = get_bankroll()

    if bankroll:
        starting_balance, current_balance, currency = bankroll
    else:
        starting_balance, current_balance, currency = 0.0, 0.0, "EUR"

    profit = current_balance - starting_balance

    if starting_balance > 0:
        profit_percent = (profit / starting_balance) * 100
    else:
        profit_percent = 0.0

    if profit_percent > 0:
        trend_icon = "↗"
        trend_color = "#10B981"
    elif profit_percent < 0:
        trend_icon = "↘"
        trend_color = "#EF4444"
    else:
        trend_icon = "→"
        trend_color = "#6B7280"

    currency_symbols = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£",
    }

    currency_symbol = currency_symbols.get(
        currency,
        currency,
    )

    html = dedent(
        f"""
        <div style="
            display:flex;
            align-items:center;
            justify-content:space-between;
            padding:22px 30px;
            border-radius:22px;
            background:#ffffff;
            box-shadow:0 12px 35px rgba(0,0,0,0.08);
            font-family:Arial, sans-serif;
        ">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="
                    width:54px;
                    height:54px;
                    border-radius:50%;
                    background:#10B981;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:white;
                    font-size:28px;
                ">⚽</div>

                <div>
                    <div style="
                        font-size:28px;
                        font-weight:900;
                        color:#111827;
                    ">
                        BetLab <span style="color:#10B981;">AI</span>
                    </div>

                    <div style="
                        font-size:13px;
                        color:#6B7280;
                    ">
                        Football Intelligence Platform
                    </div>
                </div>
            </div>

            <div style="display:flex;align-items:center;gap:22px;">
                <div style="
                    padding:12px 18px;
                    border-radius:16px;
                    background:#F9FAFB;
                    border:1px solid #E5E7EB;
                    min-width:150px;
                ">
                    <div style="
                        font-size:12px;
                        color:#6B7280;
                    ">
                        Balance
                    </div>

                    <div style="
                        font-size:20px;
                        font-weight:900;
                        color:#111827;
                    ">
                        {currency_symbol}{current_balance:,.2f}
                    </div>

                    <div style="
                        font-size:12px;
                        color:{trend_color};
                        font-weight:700;
                    ">
                        {trend_icon} {profit_percent:+.2f}%
                    </div>
                </div>

                <div>
                    <div style="
                        font-weight:900;
                        color:#111827;
                    ">
                        Thodoris
                    </div>

                    <div style="
                        font-size:13px;
                        color:#10B981;
                        font-weight:700;
                    ">
                        Pro Plan
                    </div>
                </div>
            </div>
        </div>
        """
    )

    components.html(
        html,
        height=130,
    )