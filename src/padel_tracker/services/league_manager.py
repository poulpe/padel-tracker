"""
CRUD on Leagues
"""

import pandas as pd
import sqlalchemy
import pydantic

from padel_tracker.models.links import LinkPlayerLeague
from padel_tracker.utils.errors import (
    LeagueNotFoundError,
    LeagueExistsError,
    InvalidLeagueNameError,
    PlayerNotInLeagueError,
    PlayerAlreadyInLeagueError,
)
from padel_tracker.utils.logs import get_logger
from padel_tracker.models.players import Player
from padel_tracker.models.matches import Match
from padel_tracker.models.leagues import League
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    # delete_from_db,
)

LOGGER = get_logger("league_manager")

# GET/UPDATE


def get_league_from_name(session: Session, name: str) -> League:
    """
    Parameters
    ----------
    session:Session
        Database session
    name:str
        Player name

    Raises
    ------
    LeagueNotFoundError
        If league doesn't exist in database
    """
    try:
        league = read_from_db(
            League, where=League.name == name, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise LeagueNotFoundError(f"league '{name}' not found in database")
    return league


def assign_league_to_player(session: Session, player: Player, league: League) -> None:
    """"""
    # Check player not already in league
    for link in player.league_links:
        if link.league == league:
            raise PlayerAlreadyInLeagueError
    # Create LinkPlayerLeague
    link = LinkPlayerLeague(
        player=player, league=league, player_name=player.name, league_name=league.name
    )
    league.nb_players += 1
    commit_to_db(link, player, league, session=session)
    LOGGER.notif(f"{player=} has been assigned to {league=}")


def update_league_after_finished_match(
    session: Session,
    match: Match,
    league: League,
) -> League:
    LOGGER.debug("starting update of league")
    league.nb_matches += 1
    league.last_match_date = match.date
    commit_to_db(league, session=session)
    LOGGER.info(f"league '{league.name}' has been updated from match id={match.id}")
    return league


def get_all_leagues(
    session: Session, as_df: bool = False
) -> list[League] | pd.DataFrame:
    return read_from_db(League, session=session, as_df=as_df)


def get_all_league_names(session: Session) -> list[str]:
    return read_from_db(League.name, session=session)


def get_linkplayerleague_from_league(
    session: Session, league_name: str, as_df: bool = False
) -> list[LinkPlayerLeague] | pd.DataFrame:
    """Table with the rank and best_rank per league per player"""
    return read_from_db(
        LinkPlayerLeague,
        where=LinkPlayerLeague.league_name == league_name,
        session=session,
        as_df=as_df,
    )


# CREATE


def create_league(session: Session, name: str, **kwargs) -> League:
    logger = LOGGER  # .getChild("create_league")
    name = name[0].upper() + name[1:] if name else name  # Capitalize 1st letter
    # Checks league doesn't exist
    try:
        league = get_league_from_name(session=session, name=name)
    except LeagueNotFoundError:
        pass  # It's actually OK, league doesn't exist
    else:
        err_msg = f"League({league.name=}, {league.id=}) already exists, won't recreate"
        logger.error(err_msg)
        raise LeagueExistsError(err_msg)
    # Let's go
    try:
        league = League(name=name, **kwargs)
    except pydantic.ValidationError as exc:
        for error in exc.errors():
            if "string" in error["type"]:
                raise InvalidLeagueNameError(error["msg"])
        raise exc
    # Commit if successfull
    commit_to_db(league, session=session)
    logger.notif(f"created {league = }")
    return league


# UTILS
def check_players_all_in_league(
    # session: Session,
    players: list[Player],
    league: League,
    # logger: logging.Logger,
) -> None:
    """Raises PlayerNotInLeagueError"""
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
