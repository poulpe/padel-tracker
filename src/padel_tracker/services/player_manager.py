"""
CRUD on Players and Teams
"""

from collections import Counter

import sqlalchemy
import pandas as pd
import pydantic

from padel_tracker.utils.errors import (
    PlayerNotFoundError,
    PlayerExistsError,
    InvalidPlayerNameError,
    SamePlayerInOneTeamError,
    TeamNotFoundError,
    TeamExistsError,
)
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
    """

    Raises
    ------
    PlayerExistsError
    InvalidPlayerNameError

    """
    logger = LOGGER.getChild("create_player")
    name = name[0].upper() + name[1:] if name else name  # Capitalize 1st letter
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
    try:
        player = Player(name=name, **kwargs)
    except pydantic.ValidationError as exc:
        for error in exc.errors():
            if "string" in error["type"]:
                raise InvalidPlayerNameError(error["msg"])
        raise exc
    # Commit if successfull
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


def get_all_teams(session: Session, as_df: bool = False) -> list[Team] | pd.DataFrame:
    return read_from_db(Team, session=session, as_df=as_df)


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


##### Interactions ######
def get_best_teammate(player_name: str, df_teams: pd.DataFrame) -> tuple[str, int]:
    """Returns teammate player with the most common wins and the nb of victories"""
    df_teams = df_teams[df_teams["name"].str.contains(player_name, na=False)]
    ## Best teammate (player with the most common wins)
    idx_best_teammate = df_teams["nb_victories"].idxmax()
    best_team_name = df_teams.loc[idx_best_teammate, "name"]
    nb_victories_best = int(df_teams.loc[idx_best_teammate, "nb_victories"])
    best_teammate_name = None
    for name in best_team_name.split("/"):
        if name != player_name:
            best_teammate_name = name
    return best_teammate_name, nb_victories_best


def get_most_played_teammate(
    player_name: str, df_teams: pd.DataFrame
) -> tuple[str, int]:
    """Returns teammate player with the most common matches and the nb of matches"""
    df_teams = df_teams[df_teams["name"].str.contains(player_name, na=False)]
    idx_most_teammate = df_teams["nb_matches"].idxmax()
    most_team_name = df_teams.loc[idx_most_teammate, "name"]
    nb_matches_most = int(df_teams.loc[idx_most_teammate, "nb_matches"])
    most_teammate_name = None
    for name in most_team_name.split("/"):
        if name != player_name:
            most_teammate_name = name
    return most_teammate_name, nb_matches_most


def get_black_beast_and_favorite_victim(
    player_name: str, df_matches: pd.DataFrame
) -> tuple[str, int, str, int]:
    """Returns opponent player against lost the most and won the most.
    Also returns the nb of defeats against black beast and nb of victories against favorite victim.

    Returns
    -------
    black_beast:str
        Player against lost the most
    nb_defeats_black_beast:int
        Nb of defeats against black beast
    favorite_victim:str
        Player against won the most
    nb_victories_favorite_victim:int
        Nb of victories against favorite victim
    """
    df_matches = df_matches[df_matches["name"].str.contains(player_name, na=False)]

    loss_counter = Counter()
    win_counter = Counter()
    for _, row in df_matches.iterrows():
        # Parse team names
        team1, team2 = row["name"].split(" vs ")
        team1_players = set(team1.split("/"))
        team2_players = set(team2.split("/"))

        if player_name in team1_players:
            if not row["team1_won"]:  # Player was in team1 and lost
                loss_counter.update(team2_players)
            else:  # Player was in team1 and won
                win_counter.update(team2_players)
        elif player_name in team2_players:
            if row["team1_won"]:  # Player was in team2 and lost
                loss_counter.update(team1_players)
            else:  # Player was in team2 and won
                win_counter.update(team1_players)

    # Find the opponent with the most losses and wins
    if loss_counter:
        black_beast = max(loss_counter, key=loss_counter.get)
        nb_defeats_black_beast = loss_counter[black_beast]
    else:
        black_beast = None
        nb_defeats_black_beast = 0

    if win_counter:
        favorite_victim = max(win_counter, key=win_counter.get)
        nb_victories_favorite_victim = win_counter[favorite_victim]
    else:
        favorite_victim = None
        nb_victories_favorite_victim = 0

    return (
        black_beast,
        nb_defeats_black_beast,
        favorite_victim,
        nb_victories_favorite_victim,
    )
