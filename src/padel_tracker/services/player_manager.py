"""
CRUD on Players and Teams
"""

import sqlalchemy

from padel_tracker.models.players import Player, Team
from padel_tracker.database.db import (
    Session,
    get_db_session,
    commit_to_db,
    read_from_db,
    # delete_from_db,
)


##### Players #####
class PlayerExistsError(Exception):
    """Player already exists in database"""


class PlayerNotFoundError(Exception):
    """Player not found and probably doesn't exist in database"""


def get_player_from_name(session: Session, player_name: str) -> Player:
    """
    Parameters
    ----------
    session:Session
        Database session
    player_name:str
        Player name

    Raises
    ------
    PlayerNotFoundError
        If player doesn't exist in database
    """
    try:
        player = read_from_db(
            Player, where=Player.name == player_name, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise PlayerNotFoundError(f"player '{player_name}' not found in database")
    return player


def create_player(session: Session, name: str, **kwargs) -> Player:
    # Checks player doesn't exist
    try:
        player = get_player_from_name(session=session, player_name=name)
    except PlayerNotFoundError:
        pass  # It's actually OK, player doesn't exists
    else:
        raise PlayerExistsError(f"player '{str(player)}' already exists, won't create")
    # Let's go
    player = Player(name=name, **kwargs)
    commit_to_db(player, session=session)
    return player


# TODO: delete player
def delete_player() -> None:
    raise NotImplementedError


##### Team ######


class TeamExistsError(Exception):
    """Team already exists in database"""


class TeamNotFoundError(Exception):
    """Tean not found and probably doesn't exist in database"""


def get_team_from_players_name(
    session: Session, player1_name: str, player2_name: str
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

    Raises
    ------
    TeamNotFoundError
        If team doesn't exist in database
    """
    team_name = Team.get_name_from_players_name(player1_name, player2_name)
    try:
        team = read_from_db(
            Team, where=Team.name == team_name, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise TeamNotFoundError(
            f"team '{team_name}' not found in database, probably doesn't exist"
        )
    return team


def create_team(session: Session, player1_name: str, player2_name: str) -> Team:
    # Checks team doesn't exist
    try:
        team = get_team_from_players_name(
            session=session, player1_name=player1_name, player2_name=player2_name
        )
    except TeamNotFoundError:
        pass  # It's actually OK, team doesn't exists
    else:
        raise TeamExistsError(f"team '{str(team)}' already exists, won't recreate it")
    # Let's go
    ## Retrieve players
    player1 = get_player_from_name(session=session, player_name=player1_name)
    player2 = get_player_from_name(session=session, player_name=player2_name)
    ## Create team and commit
    team = Team(players=[player1, player2])
    team.post_init()
    commit_to_db(team, session=session)
    return team


def delete_team() -> None:
    raise NotImplementedError("no real point of deleting a team ?")


if __name__ == "__main__":
    with get_db_session() as session:
        try:
            team = get_team_from_players_name(session, "p6", "p2")
        except sqlalchemy.exc.NoResultFound or sqlalchemy.exc:
            print("it's OK")
