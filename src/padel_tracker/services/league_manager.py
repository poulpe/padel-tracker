"""
CRUD on Leagues
"""

import logging

import pandas as pd
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


# TODO (prio2) :assign_league_to_player
def assign_league_to_player(session: Session, player: Player, league: League) -> Player:
    pass


# TOCHECK: update_league
def update_league_after_finished_match(
    session: Session,
    match: Match,
    league: League,
) -> League:
    league.nb_matches += 1
    league.last_match_date = match.date
    commit_to_db(league, session=session)
    return league


def get_all_leagues(
    session: Session, as_df: bool = False
) -> list[League] | pd.DataFrame:
    return read_from_db(League, session=session, as_df=as_df)


def get_all_league_names(session: Session) -> list[str]:
    return read_from_db(League.name, session=session)


# CREATE


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


# UTILS


# TODO (prio1) :check_players_all_in_league
def check_players_all_in_league(
    session: Session,
    players: list[Player],
    league: League,
    logger: logging.Logger,
) -> None:
    """Raises PlayerNotInLeagueError"""
    pass
