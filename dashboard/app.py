import sqlite3
import sys
from pathlib import Path

import streamlit as st

sys.path.append(".")

from dashboard.analyzer import render_analyzer_page
from dashboard.bet_tracker import render_bet_tracker
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

tab1, tab2, tab3 = st.tabs(["🔥 Today's Picks", "🔍 Analyzer", "📒 Bet Tracker"])

with tab1:
    render_today_picks()

with tab2:
    render_analyzer_page(teams)

with tab3:
    render_bet_tracker()

st.divider()
st.caption("BetLab AI Pro v0.2 • © 2026 • Developed by Thodoris Vallianos")