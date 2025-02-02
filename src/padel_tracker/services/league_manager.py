"""
CRUD on Leagues
"""

import logging

import sqlalchemy
import pydantic

from padel_tracker.utils.errors import (
    LeagueNotFoundError,
    LeagueExistsError,
    InvalidLeagueNameError,
    # PlayerNotInLeagueError,
    # TeamExistsError,
)
from padel_tracker.utils.logs import get_logger, LOG_LEVEL_NOTIF
from padel_tracker.models.players import Player
from padel_tracker.models.leagues import League
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    # delete_from_db,
)

LOGGER = get_logger("league_manager")


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
    PlayerNotFoundError
        If player doesn't exist in database
    """
    try:
        league = read_from_db(
            League, where=League.name == name, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise LeagueNotFoundError(f"league '{name}' not found in database")
    return league


def create_league(session: Session, name: str, **kwargs) -> League:
    logger = LOGGER.getChild("create_league")
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
    logger.log(LOG_LEVEL_NOTIF, f"created {league = }")
    return league


# TODO
def check_players_all_in_league(
    session: Session,
    players: list[Player],
    league: League,
    logger: logging.Logger,
) -> None:
    """Raises PlayerNotInLeagueError"""
    pass
