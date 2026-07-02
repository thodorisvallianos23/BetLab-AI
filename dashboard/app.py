import sqlite3
import sys
from pathlib import Path

import streamlit as st

sys.path.append(".")

from dashboard.analyzer import render_analyzer_page
from dashboard.bet_tracker import render_bet_tracker
from dashboard.home import render_home
from dashboard.today_picks import render_today_picks
from dashboard.top_nav import render_top_nav

DB_PATH = Path("data/betlab_v2.db")


def get_teams():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT team_name FROM teams ORDER BY team_name")
    teams = [row[0] for row in cursor.fetchall()]
    conn.close()
    return teams


st.set_page_config(page_title="BetLab AI Pro", layout="wide")

render_top_nav()

teams = get_teams()

page = st.segmented_control(
    "Navigation",
    ["🏠 Home", "🔥 Today's Picks", "🔍 Analyzer", "📒 Bet Tracker", "📊 Insights", "⚙️ Settings"],
    label_visibility="collapsed",
)

st.divider()

if page == "🏠 Home":
    render_home()
elif page == "🔥 Today's Picks":
    render_today_picks()
elif page == "🔍 Analyzer":
    render_analyzer_page(teams)
elif page == "📒 Bet Tracker":
    render_bet_tracker()
elif page == "📊 Insights":
    st.info("📊 Insights page coming soon.")
elif page == "⚙️ Settings":
    st.info("⚙️ Settings page coming soon.")
else:
    render_home()

st.divider()
st.caption("BetLab AI Pro v0.2 • © 2026 • Developed by Thodoris Vallianos")