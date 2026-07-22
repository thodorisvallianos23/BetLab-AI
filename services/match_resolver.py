from database.team_lookup import (
    get_team_id,
    get_league_id,
    get_season_id,
)


def resolve_match(
    home_team,
    away_team,
    league_name,
    season_name="2026/2027",
):
    return {
        "home_team_id": get_team_id(home_team),
        "away_team_id": get_team_id(away_team),
        "league_id": get_league_id(league_name),
        "season_id": get_season_id(season_name),
    }