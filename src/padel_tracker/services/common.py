from padel_tracker.utils.errors import PlayerNotInLeagueError
from padel_tracker.models.players import Player
from padel_tracker.models.leagues import League


# UTILS
def check_players_all_in_league(
    players: list[Player],
    league: League,
) -> None:
    """Raises PlayerNotInLeagueError if not"""
    list_is_in = []
    for player in players:
        is_in = False
        for link in player.league_links:
            if link.league == league:
                is_in = True
                break
        list_is_in.append(is_in)
    if not all(list_is_in):
        raise PlayerNotInLeagueError
