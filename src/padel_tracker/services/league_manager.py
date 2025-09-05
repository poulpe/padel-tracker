"""
CRUD on Leagues
"""

import pandas as pd
import sqlalchemy
import pydantic

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import (
    LeagueNotFoundError,
    LeagueExistsError,
    InvalidLeagueNameError,
    PlayerNotInLeagueError,
    PlayerAlreadyInLeagueError,
)
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.models.links import LinkPlayerLeague
from padel_tracker.models.players import Player
from padel_tracker.models.leagues import League
from padel_tracker.models.users import User
from padel_tracker.services import user_manager, match_manager

LOGGER_NAME = "leagues"
LOGGER = get_logger(LOGGER_NAME)

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


def get_all_leagues(
    session: Session, as_df: bool = False
) -> list[League] | pd.DataFrame:
    return read_from_db(League, session=session, as_df=as_df)


def get_all_public_leagues(
    session: Session, as_df: bool = False
) -> list[League] | pd.DataFrame:
    return read_from_db(
        League,
        where=League.is_private == False,  # noqa: E712
        session=session,
        as_df=as_df,
    )


def get_all_private_leagues(
    session: Session, as_df: bool = False
) -> list[League] | pd.DataFrame:
    return read_from_db(
        League,
        where=League.is_private == True,  # noqa: E712
        session=session,
        as_df=as_df,
    )


def get_all_leagues_from_player(
    session: Session,
    player_name: str,
    as_df: bool = False,
    order_by=None,
    order_descending: bool = False,
) -> list[League] | pd.DataFrame:
    # First fetch league IDs from LinkPlayerLeague
    league_ids = read_from_db(
        LinkPlayerLeague.league_id,
        where=LinkPlayerLeague.player_name == player_name,
        session=session,
    )
    # Then get players with corresponding IDs
    return read_from_db(
        League,
        where=League.id.in_(league_ids),
        session=session,
        as_df=as_df,
        order_by=order_by,
        order_descending=order_descending,
    )


def get_all_league_names(session: Session) -> list[str]:
    return read_from_db(League.name, session=session)


def get_admin_names_from_league_name(session, name: str) -> list[str]:
    league = get_league_from_name(session=session, name=name)
    return [user.name for user in league.admin_users]


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
    LOGGER.success(f"{player=} has been assigned to {league=}")


def remove_player_from_league(session: Session, player: Player, league: League) -> None:
    # Fetch link
    link_to_delete = None
    for link in player.league_links:
        if link.league == league:
            link_to_delete = link
            break
    if not link_to_delete:
        raise PlayerNotInLeagueError
    # Unlink
    league.nb_players -= 1
    commit_to_db(league, session=session)
    # Delete link
    delete_from_db(link_to_delete, session=session)
    LOGGER.success(f"{player=} has been removed from {league=}")


def assign_admin_to_league(session: Session, user: User, league: League) -> None:
    """And add associated player to league if not already in"""
    league.admin_users.append(user)
    user.admin_leagues.append(league)
    # Add associated player to league
    try:
        assign_league_to_player(session, player=user.player, league=league)
    except PlayerAlreadyInLeagueError:
        pass
    # If user doesn't have a default league, make it default
    if not user.default_league_name:
        user.default_league_name = league.name
    commit_to_db(league, user, session=session)
    LOGGER.success(f"assigned user='{user.name}' as admin of league='{league.name}'")


def make_league_private(session: Session, league: League) -> None:
    if not league.is_private:
        league.is_private = True
        commit_to_db(league, session=session)
        LOGGER.success(f"league '{league.name}' has been made 'private'")
    else:
        raise ValueError(f"league '{league.name}' is already 'private'")


def make_league_public(session: Session, league: League) -> None:
    if league.is_private:
        league.is_private = False
        commit_to_db(league, session=session)
        LOGGER.success(f"league '{league.name}' has been made 'public'")
    else:
        raise ValueError(f"league '{league.name}' is already 'public'")


def update_league_description(
    session: Session, league: League, description: str
) -> None:
    league.description = description
    commit_to_db(league, session=session)


# CREATE


def create_league(
    session: Session,
    name: str,
    is_private: bool = False,
    admin_name: str = "",
    **kwargs,
) -> League:
    logger = get_logger(f"{LOGGER_NAME}.create")
    # Clean name (capitalize 1st letter + remove leading/trailing space)
    name = (name[0].upper() + name[1:]).strip() if name else name
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
        league = League(name=name, is_private=is_private, **kwargs)
    except pydantic.ValidationError as exc:
        for error in exc.errors():
            if "string" in error["type"]:
                raise InvalidLeagueNameError(error["msg"])
        raise exc
    # Commit if successfull
    commit_to_db(league, session=session)
    logger.success(f"created {league = }")
    # Assign admin
    if admin_name:
        admin_user = user_manager.get_user_from_name(session=session, name=admin_name)
        assign_admin_to_league(session=session, league=league, user=admin_user)
    return league


# DELETE
def delete_league(session: Session, name: str) -> None:
    logger = get_logger(f"{LOGGER_NAME}.delete")

    # Fetch league
    try:
        league = get_league_from_name(session=session, name=name)
    except LeagueNotFoundError:
        err_msg = f"{name} doesn't exist, cannot delete it"
        logger.error(err_msg)
        raise LeagueNotFoundError(err_msg)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)

    # Delete all player_links from league
    try:
        links = league.player_links
        delete_from_db(*links, session=session)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)

    # Update affected users "default_league_name"
    users = read_from_db(User, where=User.default_league_name == name, session=session)
    if users:
        for user in users:
            user.default_league_name = None
        commit_to_db(*users, session=session)

    # Delete all matches (solving dependencies with eloratinghistory)
    logger.info("deleting all matches from league before deleting it")
    for match in league.matches:
        match_manager.delete_match(session=session, match_id=match.id)

    # Delete
    delete_from_db(league, session=session)
    logger.success(f"deleted '{name}' successfully from database")
