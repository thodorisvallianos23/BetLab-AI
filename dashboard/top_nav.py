import streamlit.components.v1 as components
from textwrap import dedent


def render_top_nav():
    html = dedent("""
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
                <div style="font-size:28px;font-weight:900;color:#111827;">
                    BetLab <span style="color:#10B981;">AI</span>
                </div>
                <div style="font-size:13px;color:#6B7280;">
                    Football Intelligence Platform
                </div>
            </div>
        </div>

        <div style="display:flex;gap:26px;font-weight:700;color:#374151;">
            <span>🔥 Today's Picks</span>
            <span>🔍 Analyzer</span>
            <span>📒 Bet Tracker</span>
            <span>📊 Insights</span>
            <span>⚙️ Settings</span>
        </div>

        <div style="display:flex;align-items:center;gap:22px;">
            <div style="
                padding:12px 18px;
                border-radius:16px;
                background:#F9FAFB;
                border:1px solid #E5E7EB;
            ">
                <div style="font-size:12px;color:#6B7280;">Balance</div>
                <div style="font-size:20px;font-weight:900;color:#111827;">€1,250.00</div>
                <div style="font-size:12px;color:#10B981;font-weight:700;">↗ +8.4%</div>
            </div>

            <div>
                <div style="font-weight:900;color:#111827;">Thodoris</div>
                <div style="font-size:13px;color:#10B981;font-weight:700;">Pro Plan</div>
            </div>
        </div>
    </div>
    """)

    components.html(html, height=130)