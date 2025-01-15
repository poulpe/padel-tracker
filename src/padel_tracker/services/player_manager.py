"""
CRUD on Players and Teams
"""
from uuid import UUID
from datetime import datetime

import sqlalchemy
from pydantic import validate_call

from padel_tracker.models.players import Player, Team
from padel_tracker.database.db import Session, get_db_session, commit_to_db, read_from_db, delete_from_db

##### Players #####
class PlayerExistsError(Exception):
    """Player already exists in database"""

def get_player_from_name(player_name:str, session:Session) -> Player:
    player = read_from_db(Player, where=Player.name==player_name, unique=True, session=session)
    return player

def create_player(player_name:str, session:Session) -> Player:
    # Checks player doesn't exist
    try:
        player = get_player_from_name(player_name, session=session)
    except sqlalchemy.exc.NoResultFound:
        pass # It's actually OK, team doesn't exists
    else:
        raise PlayerExistsError(f"player '{str(player)}' already exists, won't create it")
    # Let's go
    player = Player(name=player_name)
    commit_to_db(player, session=session)
    return player

#TODO: delete player
def delete_player() -> None:
    raise NotImplementedError

##### Team ######

class TeamExistsError(Exception):
    """Team already exists in database"""

def get_team_from_players_name(player1_name:str, player2_name:str, session:Session) -> Team:
    team_name = Team.get_name_from_players_name(player1_name, player2_name)
    team = read_from_db(Team, where=Team.name==team_name, unique=True, session=session)
    return team

def create_team(player1_name:str, player2_name:str, session:Session) -> Team:
    # Checks team doesn't exist
    try:
        team = get_team_from_players_name(player1_name, player2_name, session)
    except sqlalchemy.exc.NoResultFound:
        pass # It's actually OK, team doesn't exists
    else:
        raise TeamExistsError(f"team '{str(team)}' already exists, won't recreate it")
    # Let's go
    ## Retrieve players
    player1 = get_player_from_name(player_name=player1_name, session=session)
    player2 = get_player_from_name(player_name=player1_name, session=session)
    ## Create team and commit
    team = Team(players=[player1, player2])
    commit_to_db(team, session=session)
    return team

def delete_team() -> None:
    raise NotImplementedError("no real point of deleting a team ?")

if __name__ == "__main__":
    with get_db_session() as session:
        try:
            team = get_team_from_players_name("p6", "p2", session)
        except sqlalchemy.exc.NoResultFound or sqlalchemy.exc:
            print("it's OK")