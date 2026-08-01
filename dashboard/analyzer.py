from dataclasses import asdict
from html import escape
from textwrap import dedent

import pandas as pd
import streamlit as st

from dashboard.sidebar import render_analyzer_controls
from models.prediction_engine import predict_match
from models.value_engine import analyze_market
from services.match_resolver import resolve_match


def safe_text(value):
    return escape(str(value))


def render_html(html):
    compact_html = "\n".join(
        line.strip()
        for line in dedent(html).splitlines()
        if line.strip()
    )

    st.markdown(
        compact_html,
        unsafe_allow_html=True,
    )


def probability_to_fair_odds(probability):
    probability = float(probability)

    if probability <= 0:
        return 0.0

    return 1.0 / probability


def prediction_to_dict(prediction_result):
    prediction = asdict(prediction_result)

    prediction.update(
        {
            "home_xg": prediction["home_expected_goals"],
            "away_xg": prediction["away_expected_goals"],
            "total_xg": prediction["total_expected_goals"],

            "home_win": prediction["home_win_probability"],
            "draw": prediction["draw_probability"],
            "away_win": prediction["away_win_probability"],

            "over_15": prediction["over_15_probability"],
            "under_15": prediction["under_15_probability"],
            "over_25": prediction["over_25_probability"],
            "under_25": prediction["under_25_probability"],
            "over_35": prediction["over_35_probability"],
            "under_35": prediction["under_35_probability"],

            "btts_yes": prediction["btts_yes_probability"],
            "btts_no": prediction["btts_no_probability"],

            "fair_home": prediction["fair_home_odds"],
            "fair_draw": prediction["fair_draw_odds"],
            "fair_away": prediction["fair_away_odds"],

            "fair_over_15": prediction["fair_over_15_odds"],
            "fair_under_15": prediction["fair_under_15_odds"],
            "fair_over_25": prediction["fair_over_25_odds"],
            "fair_under_25": prediction["fair_under_25_odds"],
            "fair_over_35": prediction["fair_over_35_odds"],
            "fair_under_35": prediction["fair_under_35_odds"],

            "fair_btts_yes": prediction["fair_btts_yes_odds"],
            "fair_btts_no": prediction["fair_btts_no_odds"],
        }
    )

    strongest_probability = max(
        prediction["home_win"],
        prediction["draw"],
        prediction["away_win"],
        prediction["over_15"],
        prediction["over_25"],
        prediction["over_35"],
        prediction["btts_yes"],
    )

    prediction["confidence"] = strongest_probability * 100
    prediction["stars"] = max(
        1,
        min(
            5,
            round(prediction["confidence"] / 20),
        ),
    )

    return prediction


def get_market_probability(
    prediction,
    selected_market,
    market_label,
):
    label = str(market_label).lower()
    selected = str(selected_market).lower()

    if selected == "match result":
        if "draw" in label or "ισοπαλία" in label:
            return prediction["draw"]

        if (
            "away" in label
            or "φιλοξενούμεν" in label
            or label.strip() == "2"
        ):
            return prediction["away_win"]

        return prediction["home_win"]

    if selected == "btts":
        if "no" in label or "όχι" in label:
            return prediction["btts_no"]

        return prediction["btts_yes"]

    if "1.5" in label:
        if "under" in label:
            return prediction["under_15"]

        return prediction["over_15"]

    if "3.5" in label:
        if "under" in label:
            return prediction["under_35"]

        return prediction["over_35"]

    if "under" in label:
        return prediction["under_25"]

    return prediction["over_25"]


def format_score_prediction(score):
    if not isinstance(score, dict):
        return None

    home_goals = score.get(
        "home_goals",
        score.get("home_score"),
    )
    away_goals = score.get(
        "away_goals",
        score.get("away_score"),
    )
    probability = float(
        score.get("probability", 0.0)
    )

    if home_goals is None or away_goals is None:
        return None

    return {
        "Score": f"{home_goals}-{away_goals}",
        "Probability": probability * 100,
        "Fair Odds": probability_to_fair_odds(
            probability
        ),
    }


def render_analyzer_styles():
    render_html(
        """
        <style>
            .betlab-analyzer-header {
                margin: 4px 0 24px 0;
            }

            .betlab-analyzer-eyebrow {
                color: #10B981;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 7px;
            }

            .betlab-analyzer-title {
                color: #111827;
                font-size: 32px;
                line-height: 1.1;
                font-weight: 900;
                letter-spacing: -0.04em;
            }

            .betlab-analyzer-subtitle {
                color: #6B7280;
                font-size: 15px;
                margin-top: 8px;
            }

            .betlab-analysis-card {
                border: 1px solid #DDE5E2;
                border-radius: 24px;
                padding: 24px;
                margin: 16px 0;
                background:
                    linear-gradient(
                        135deg,
                        rgba(16, 185, 129, 0.10),
                        rgba(255, 255, 255, 0.98) 48%
                    );
                box-shadow:
                    0 16px 38px rgba(15, 23, 42, 0.07);
            }

            .betlab-analysis-label {
                color: #047857;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .betlab-analysis-match {
                color: #111827;
                font-size: 27px;
                font-weight: 900;
                letter-spacing: -0.035em;
                margin-top: 8px;
            }

            .betlab-analysis-meta {
                color: #6B7280;
                font-size: 13px;
                margin-top: 7px;
            }

            .betlab-section-title {
                color: #111827;
                font-size: 21px;
                font-weight: 900;
                letter-spacing: -0.025em;
                margin: 24px 0 12px 0;
            }

            .betlab-value-positive {
                padding: 14px 16px;
                border: 1px solid #A7F3D0;
                border-radius: 14px;
                background: #ECFDF5;
                color: #047857;
                font-weight: 800;
                margin-top: 12px;
            }

            .betlab-value-negative {
                padding: 14px 16px;
                border: 1px solid #FCD34D;
                border-radius: 14px;
                background: #FFFBEB;
                color: #92400E;
                font-weight: 800;
                margin-top: 12px;
            }
        </style>
        """
    )


def render_page_header():
    render_html(
        """
        <div class="betlab-analyzer-header">
            <div class="betlab-analyzer-eyebrow">
                BetLab Match Intelligence
            </div>

            <div class="betlab-analyzer-title">
                Match Analyzer
            </div>

            <div class="betlab-analyzer-subtitle">
                Compare teams, calculate calibrated probabilities
                and evaluate bookmaker value.
            </div>
        </div>
        """
    )


def render_match_header(
    home_team,
    away_team,
    prediction,
):
    render_html(
        f"""
        <div class="betlab-analysis-card">
            <div class="betlab-analysis-label">
                AI Match Analysis
            </div>

            <div class="betlab-analysis-match">
                {safe_text(home_team)}
                vs
                {safe_text(away_team)}
            </div>

            <div class="betlab-analysis-meta">
                Model: {safe_text(prediction["model_name"])}
                · Confidence:
                {prediction["confidence"]:.1f}%
                · Rating:
                {"⭐" * prediction["stars"]}
            </div>
        </div>
        """
    )


def render_xg_summary(prediction):
    render_html(
        '<div class="betlab-section-title">'
        "Expected Goals Summary"
        "</div>"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Home xG",
        f"{prediction['home_xg']:.2f}",
    )

    col2.metric(
        "Away xG",
        f"{prediction['away_xg']:.2f}",
    )

    col3.metric(
        "Total xG",
        f"{prediction['total_xg']:.2f}",
    )

    col4.metric(
        "Confidence",
        f"{prediction['confidence']:.1f}%",
        f"{prediction['stars']}/5",
    )


def render_outcome_probabilities(prediction):
    render_html(
        '<div class="betlab-section-title">'
        "Match Outcome Probabilities"
        "</div>"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Home Win",
        f"{prediction['home_win'] * 100:.2f}%",
        f"Fair {prediction['fair_home']:.2f}",
    )

    col2.metric(
        "Draw",
        f"{prediction['draw'] * 100:.2f}%",
        f"Fair {prediction['fair_draw']:.2f}",
    )

    col3.metric(
        "Away Win",
        f"{prediction['away_win'] * 100:.2f}%",
        f"Fair {prediction['fair_away']:.2f}",
    )

    outcome_df = pd.DataFrame(
        {
            "Outcome": [
                "Home Win",
                "Draw",
                "Away Win",
            ],
            "Probability": [
                prediction["home_win"] * 100,
                prediction["draw"] * 100,
                prediction["away_win"] * 100,
            ],
        }
    )

    st.bar_chart(
        outcome_df.set_index("Outcome")
    )


def render_goals_markets(prediction):
    render_html(
        '<div class="betlab-section-title">'
        "Goals Markets"
        "</div>"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Over 1.5",
        f"{prediction['over_15'] * 100:.2f}%",
        f"Fair {prediction['fair_over_15']:.2f}",
    )

    col2.metric(
        "Over 2.5",
        f"{prediction['over_25'] * 100:.2f}%",
        f"Fair {prediction['fair_over_25']:.2f}",
    )

    col3.metric(
        "Over 3.5",
        f"{prediction['over_35'] * 100:.2f}%",
        f"Fair {prediction['fair_over_35']:.2f}",
    )

    under1, under2, under3 = st.columns(3)

    under1.metric(
        "Under 1.5",
        f"{prediction['under_15'] * 100:.2f}%",
        f"Fair {prediction['fair_under_15']:.2f}",
    )

    under2.metric(
        "Under 2.5",
        f"{prediction['under_25'] * 100:.2f}%",
        f"Fair {prediction['fair_under_25']:.2f}",
    )

    under3.metric(
        "Under 3.5",
        f"{prediction['under_35'] * 100:.2f}%",
        f"Fair {prediction['fair_under_35']:.2f}",
    )


def render_btts(prediction):
    render_html(
        '<div class="betlab-section-title">'
        "Both Teams To Score"
        "</div>"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "BTTS Yes",
        f"{prediction['btts_yes'] * 100:.2f}%",
        f"Fair {prediction['fair_btts_yes']:.2f}",
    )

    col2.metric(
        "BTTS No",
        f"{prediction['btts_no'] * 100:.2f}%",
        f"Fair {prediction['fair_btts_no']:.2f}",
    )


def render_correct_scores(prediction):
    top_scores = prediction.get("top_scores", [])

    rows = []

    for score in top_scores:
        formatted = format_score_prediction(score)

        if formatted:
            rows.append(formatted)

    if not rows:
        return

    render_html(
        '<div class="betlab-section-title">'
        "Most Likely Correct Scores"
        "</div>"
    )

    score_df = pd.DataFrame(rows)

    st.dataframe(
        score_df,
        hide_index=True,
        width="stretch",
        column_config={
            "Probability": st.column_config.NumberColumn(
                "Probability",
                format="%.2f%%",
            ),
            "Fair Odds": st.column_config.NumberColumn(
                "Fair Odds",
                format="%.2f",
            ),
        },
    )

    st.bar_chart(
        score_df.set_index("Score")["Probability"]
    )


def render_value_check(
    prediction,
    selected_market,
    market_label,
    bookmakers,
):
    render_html(
        '<div class="betlab-section-title">'
        "Bookmaker Value Check"
        "</div>"
    )

    model_probability = get_market_probability(
        prediction,
        selected_market,
        market_label,
    )

    fair_market_odds = probability_to_fair_odds(
        model_probability
    )

    try:
        value = analyze_market(
            model_probability,
            bookmakers,
        )
    except Exception as error:
        st.error(
            f"Could not complete value analysis: {error}"
        )
        return

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Selected Market",
        market_label,
    )

    col2.metric(
        "Model Probability",
        f"{model_probability * 100:.2f}%",
    )

    col3.metric(
        "Fair Odds",
        f"{fair_market_odds:.2f}",
    )

    col4.metric(
        "Best Odds",
        f"{float(value.get('best_odds', 0.0)):.2f}",
        safe_text(
            value.get(
                "best_bookmaker",
                "N/A",
            )
        ),
    )

    edge = float(value.get("edge", 0.0))

    if edge > 0:
        message_class = "betlab-value-positive"
    else:
        message_class = "betlab-value-negative"

    decision = safe_text(
        value.get(
            "decision",
            "No decision available.",
        )
    )

    render_html(
        f"""
        <div class="{message_class}">
            Edge: {edge * 100:+.2f}% · {decision}
        </div>
        """
    )


def render_analyzer_page(teams, leagues):
    render_analyzer_styles()
    render_page_header()

    (
        selected_league,
        home_team,
        away_team,
        selected_market,
        market_label,
        bookmakers,
        predict_button,
    ) = render_analyzer_controls(
        teams,
        leagues,
    )

    if not predict_button:
        st.info(
            "Διάλεξε τις δύο ομάδες, συμπλήρωσε τις "
            "αποδόσεις και πάτησε Predict Match."
        )
        return

    if home_team == away_team:
        st.error(
            "Home Team και Away Team δεν μπορούν "
            "να είναι η ίδια ομάδα."
        )
        return

    resolved = resolve_match(
        home_team,
        away_team,
        selected_league,
        None,
    )

    if any(
        resolved[key] is None
        for key in (
            "home_team_id",
            "away_team_id",
            "league_id",
            "season_id",
        )
    ):
        st.error(
            "Δεν ήταν δυνατή η αντιστοίχιση των ομάδων, "
            "της λίγκας ή της σεζόν με τη βάση δεδομένων."
        )

        st.write(resolved)
        return

    try:
        prediction_result = predict_match(
            home_team_id=resolved["home_team_id"],
            away_team_id=resolved["away_team_id"],
            league_id=resolved["league_id"],
            season_id=resolved["season_id"],
        )

        prediction = prediction_to_dict(
            prediction_result
        )

    except Exception as error:
        st.error(
            f"Could not calculate prediction: {error}"
        )
        return

    render_match_header(
        home_team,
        away_team,
        prediction,
    )

    render_xg_summary(prediction)
    render_outcome_probabilities(prediction)
    render_goals_markets(prediction)
    render_btts(prediction)
    render_correct_scores(prediction)

    render_value_check(
        prediction=prediction,
        selected_market=selected_market,
        market_label=market_label,
        bookmakers=bookmakers,
    )