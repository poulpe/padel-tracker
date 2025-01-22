"""
CRUD on Players and Teams
"""

import sqlalchemy
import pandas as pd

from padel_tracker.utils.logs import get_logger, LOG_LEVEL_NOTIF
from padel_tracker.models.players import Player, Team
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
    # delete_from_db,
)

LOGGER = get_logger("player_manager")


##### Players #####
class PlayerExistsError(Exception):
    """Player already exists in database"""


class PlayerNotFoundError(Exception):
    """Player not found and probably doesn't exist in database"""


def get_player_from_name(session: Session, name: str) -> Player:
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
        player = read_from_db(
            Player, where=Player.name == name, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise PlayerNotFoundError(f"player '{name}' not found in database")
    return player


def get_all_players(
    session: Session, as_df: bool = False
) -> list[Player] | pd.DataFrame:
    return read_from_db(Player, session=session, as_df=as_df)


def create_player(session: Session, name: str, **kwargs) -> Player:
    logger = LOGGER.getChild("create_player")
    # Checks player doesn't exist
    try:
        player = get_player_from_name(session=session, name=name)
    except PlayerNotFoundError:
        pass  # It's actually OK, player doesn't exists
    else:
        err_msg = f"Player({player.name=}, {player.id=}) already exists, won't recreate"
        logger.error(err_msg)
        raise PlayerExistsError(err_msg)
    # Let's go
    player = Player(name=name, **kwargs)
    commit_to_db(player, session=session)
    logger.log(LOG_LEVEL_NOTIF, f"created {player = }")
    return player


def delete_player(session: Session, name: str) -> None:
    logger = LOGGER.getChild("delete_player")
    try:
        player = get_player_from_name(session=session, name=name)
        delete_from_db(player, session=session)
        logger.log(LOG_LEVEL_NOTIF, f"deleted {name} successfully from database")
    except PlayerNotFoundError:
        err_msg = f"{name} doesn't exist, cannot delete it"
        logger.error(err_msg)
        raise PlayerNotFoundError(err_msg)
    except Exception as exc:
        logger.exception(exc)


##### Team ######


class TeamExistsError(Exception):
    """Team already exists in database"""


class TeamNotFoundError(Exception):
    """Tean not found and probably doesn't exist in database"""


class SamePlayerInOneTeamError(Exception):
    """Same player have been selected to create 1 team"""


def get_team_from_players_name(
    session: Session,
    player1_name: str,
    player2_name: str,
    create_if_not_found: bool = False,
) -> Team:
    """
    Parameters
    ----------
    session:Session
        Database session
    player1_name:str
        Player1 name
    player2_name:str
        Player2 name
    create_if_not_found:bool, optional
        Create the team if it's not existing in db. Default to False,

    Raises
    ------
    TeamNotFoundError
        If team doesn't exist in database
    SamePlayerInOneTeamError:
        If player1_name == player2_name
    """
    if player1_name == player2_name:
        raise SamePlayerInOneTeamError(
            f"same player in the team. Got {player1_name=} and {player2_name=}"
        )
    team_name = Team.get_name_from_players_name(player1_name, player2_name)
    try:
        team = read_from_db(
            Team, where=Team.name == team_name, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        if create_if_not_found:
            player1 = get_player_from_name(session=session, name=player1_name)
            player2 = get_player_from_name(session=session, name=player2_name)
            ## Create team and commit
            team = Team(players=[player1, player2])
            team.post_init()
            commit_to_db(team, session=session)
        else:
            raise TeamNotFoundError(f"team '{team_name}' not found in db")
    return team


def create_team(session: Session, player1_name: str, player2_name: str) -> Team:
    logger = LOGGER.getChild("create_team")
    # Checks team doesn't exist
    try:
        team = get_team_from_players_name(
            session=session, player1_name=player1_name, player2_name=player2_name
        )
    except TeamNotFoundError:
        pass  # It's actually OK, team doesn't exists
    else:
        err_msg = f"team '{str(team)}' already exists, won't recreate it"
        logger.error(err_msg)
        raise TeamExistsError(err_msg)
    # Let's go
    ## Retrieve players
    player1 = get_player_from_name(session=session, name=player1_name)
    player2 = get_player_from_name(session=session, name=player2_name)
    ## Create team and commit
    team = Team(players=[player1, player2])
    team.post_init()
    commit_to_db(team, session=session)
    logger.log(LOG_LEVEL_NOTIF, f"created {team=} (id={team.id})")
    return team


def delete_team() -> None:
    raise NotImplementedError("no real point of deleting a team ?")
