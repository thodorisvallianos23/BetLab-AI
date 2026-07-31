from database.team_lookup import (
    get_latest_finished_season_name,
    get_league_id,
    get_season_id,
    get_team_id,
)


def resolve_match(
    home_team,
    away_team,
    league_name,
    season_name=None,
):
    league_id = get_league_id(league_name)

    if season_name is None and league_id is not None:
        season_name = get_latest_finished_season_name(
            league_id
        )

    return {
        "home_team_id": get_team_id(home_team),
        "away_team_id": get_team_id(away_team),
        "league_id": league_id,
        "season_id": (
            get_season_id(season_name)
            if season_name
            else None
        ),
    }