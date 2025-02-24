"""
CRUD on Players and Teams
"""

from collections import Counter

import sqlalchemy
import pandas as pd
import pydantic

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import (
    PlayerNotFoundError,
    PlayerExistsError,
    InvalidPlayerNameError,
    SamePlayerInOneTeamError,
    TeamNotFoundError,
)
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.models.leagues import League
from padel_tracker.models.links import LinkPlayerLeague, LinkTeamLeague
from padel_tracker.models.players import Player, Team


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


def get_all_players_names(session: Session) -> list[str]:
    """Names only as list of all players from all leagues"""
    return read_from_db(Player.name, session=session)


def get_all_players_from_league(
    session: Session,
    league_name: str,
    as_df: bool = False,
    order_by=None,
    order_descending: bool = False,
) -> list[Player] | pd.DataFrame:
    # First fetch player IDs from LinkPlayerLeague
    player_ids = read_from_db(
        LinkPlayerLeague.player_id,
        where=LinkPlayerLeague.league_name == league_name,
        session=session,
    )
    # Then get players with corresponding IDs
    return read_from_db(
        Player,
        where=Player.id.in_(player_ids),
        session=session,
        as_df=as_df,
        order_by=order_by,
        order_descending=order_descending,
    )


def get_all_players_names_from_other_leagues(
    session: Session,
    league_name_exclude: str,
) -> list[str]:
    # First fetch player IDs from LinkPlayerLeague
    player_ids = read_from_db(
        LinkPlayerLeague.player_id,
        where=LinkPlayerLeague.league_name != league_name_exclude,
        session=session,
    )
    # Then get players with corresponding IDs
    return read_from_db(
        Player.name,
        where=Player.id.in_(player_ids),
        session=session,
        as_df=False,
    )


def get_all_players_without_user(session: Session) -> list[Player]:
    condition = Player.user == None  # noqa: E711  # Didn't work with 'is None'
    return read_from_db(Player, where=condition, session=session)


def create_player(
    session: Session, name: str, league: League | list[League] = None, **kwargs
) -> Player:
    """

    Raises
    ------
    PlayerExistsError
    InvalidPlayerNameError

    """
    logger = LOGGER  # .getChild("create_player")
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
    # Assign to leagues if provided
    links = []
    if league:
        list_leagues = [league] if isinstance(league, League) else league
        for league in list_leagues:
            link = LinkPlayerLeague(
                player=player,
                league=league,
                player_name=player.name,
                league_name=league.name,
            )
            links.append(link)
            league.nb_players += 1
            links.append(league)
    # Commit if successfull
    commit_to_db(player, *links, session=session)
    logger.notif(f"created {player = }")
    return player


def delete_player(session: Session, name: str) -> None:
    logger = LOGGER  # .getChild("delete_player")
    # Fetch player
    try:
        player = get_player_from_name(session=session, name=name)
    except PlayerNotFoundError:
        err_msg = f"{name} doesn't exist, cannot delete it"
        logger.error(err_msg)
        raise PlayerNotFoundError(err_msg)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)

    # Delete linkplayerleague first
    try:
        links = player.league_links
        for link in links:
            link.league.nb_players -= 1
            delete_from_db(link, session=session)
        # Delete rank and elo_rating histories
        for row in player.elo_rating_history:
            delete_from_db(row, session=session)
        for row in player.rank_history:
            delete_from_db(row, session=session)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)

    # Finally delete player
    delete_from_db(player, session=session)
    logger.notif(f"deleted '{name}' successfully from database")


##### Team ######
def get_team_from_players_name(
    session: Session,
    player1_name: str,
    player2_name: str,
    league_name: str = None,
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
            Team,
            # join_class=LinkTeamLeague,
            # join_clause=Team.id == LinkTeamLeague.team_id,
            # where=(LinkTeamLeague.league_id == league.id, Team.name == team_name),
            where=Team.name == team_name,
            unique=True,
            session=session,
        )
    except sqlalchemy.exc.NoResultFound:
        if create_if_not_found:
            league = read_from_db(
                League, where=League.name == league_name, unique=True, session=session
            )
            player1 = get_player_from_name(session=session, name=player1_name)
            player2 = get_player_from_name(session=session, name=player2_name)
            ## Create team and commit
            team = Team(players=[player1, player2], leagues=[league])
            team.post_init()
            commit_to_db(team, league, session=session)
        else:
            raise TeamNotFoundError(f"team '{team_name}' not found in db")
    return team


def get_all_teams(session: Session, as_df: bool = False) -> list[Team] | pd.DataFrame:
    return read_from_db(Team, session=session, as_df=as_df)


def get_all_teams_from_league(
    session: Session, league_name: str, as_df: bool = False
) -> list[Team] | pd.DataFrame:
    # Fecth league
    league_id = read_from_db(
        League.id, where=League.name == league_name, unique=True, session=session
    )
    # First fetch teams IDs from LinkTeamLeague
    team_ids = read_from_db(
        LinkTeamLeague.team_id,
        where=LinkTeamLeague.league_id == league_id,
        session=session,
    )
    # Then get players with corresponding IDs
    return read_from_db(
        Team,
        where=Team.id.in_(team_ids),
        session=session,
        as_df=as_df,
    )


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


def get_team_black_beast_and_favorite_victim(
    team_name: str, df_matches: pd.DataFrame
) -> tuple[str, int, str, int]:
    """Returns opponent team against lost the most and won the most.
    Also returns the nb of defeats against black beast and nb of victories against favorite victim.

    Returns
    -------
    black_beast:str
        Team against lost the most
    nb_defeats_black_beast:int
        Nb of defeats against black beast
    favorite_victim:str
        Team against won the most
    nb_victories_favorite_victim:int
        Nb of victories against favorite victim
    """
    df_matches = df_matches[df_matches["name"].str.contains(team_name, na=False)]

    loss_counter = Counter()
    win_counter = Counter()
    for _, row in df_matches.iterrows():
        # Parse team names
        team1, team2 = row["name"].split(" vs ")

        if team_name == team1:
            if not row["team1_won"]:
                loss_counter.update({team2})
            else:
                win_counter.update({team2})
        elif team_name == team2:
            if row["team1_won"]:
                loss_counter.update({team1})
            else:
                win_counter.update({team1})

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
