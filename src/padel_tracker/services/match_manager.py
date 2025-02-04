"""
CRUD on Matches and repercussions on players/teams

'session' refers as "database session", that can be obtained via call to get_db_session()
"""

import logging
from uuid import UUID
from datetime import datetime

import pandas as pd

from padel_tracker.models.leagues import League
from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import (
    MatchExistsError,
    MatchNotFinishedError,
    SamePlayerInBothTeamsError,
)
from padel_tracker.models.players import Team, EloRatingHistory, TeamEloRatingHistory
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.services import ranking_manager, league_manager

LOGGER = get_logger("match_manager")


def process_finished_match(
    session: Session, match: Match, delete_on_error: bool = True
) -> tuple[dict[str, int], dict[str, int]]:
    try:
        dict_elo_rating_gains, dict_updated_elo_ratings = (
            ranking_manager.update_players_results_after_finished_match(
                session=session, match=match
            )
        )
        ranking_manager.update_players_rank(session=session, league=match.league)
        league_manager.update_league_after_finished_match(
            session=session, league=match.league, match=match
        )
        info_msg = f"processed finished_match id={match.id}"
        LOGGER.notif(info_msg)
    except Exception:
        # TOCHECK (prio1) : err during process_finished_match
        err_msg = "match is not finished: won't process"
        if delete_on_error:
            delete_from_db(match, session=session)
            err_msg += " and deleted it from db"
        LOGGER.error(err_msg)
        raise MatchNotFinishedError(err_msg)
    return dict_elo_rating_gains, dict_updated_elo_ratings


# CREATE


def create_match(
    session: Session,
    teams: list[Team],
    league_name: str,
    date: datetime,
    score: str | MatchScore | None = None,
    is_finished: bool = True,
) -> Match:
    """If score is not given, match will not be considered finished"""
    logger = LOGGER  # .getChild("create_match")

    # Normalize score as str for creation
    if isinstance(score, MatchScore):
        score = str(score)
    # Basic check nb teams
    nb_teams = len(teams)
    if nb_teams != 2:
        err_msg = f"a match must have exactly 2 teams. Got {nb_teams=}"
        logger.error(err_msg)
        raise ValueError(err_msg)
    for team in teams:
        nb_player = len(team.players)
        if nb_player != 2:
            err_msg = f"a team must have exactly 2 players. Got {nb_player=} in {team=}"
            logger.error(err_msg)
            raise ValueError(err_msg)
    # Checks if 1 player is in both teams
    for player in teams[0].players:
        if player in teams[1].players:
            err_msg = f"{player.name} is in both teams"
            raise SamePlayerInBothTeamsError(err_msg)
    for player in teams[1].players:
        if player in teams[0].players:
            err_msg = f"{player.name} is in both teams"
            raise SamePlayerInBothTeamsError(err_msg)

    # Fetch league
    league = read_from_db(
        League, where=League.name == league_name, session=session, unique=True
    )

    # Check match doesn't exist already
    check_match_not_already_created(
        session=session,
        teams=teams,
        date=date,
        league_name=league_name,
        score=score,
        logger=logger,
    )
    # Check players all in the same league
    players = [
        teams[0].players[0],
        teams[0].players[1],
        teams[1].players[0],
        teams[1].players[1],
    ]
    league_manager.check_players_all_in_league(
        players=players, league=league  # , session=session, logger=logger
    )

    # Create match
    match = Match(teams=teams, players=players, date=date, score=score, league=league)
    match.post_init()
    ## Commit
    commit_to_db(match, league, session=session)
    logger.notif(f"created new match id={match.id}")
    # Process it if finished
    if is_finished:
        process_finished_match(session=session, match=match)
    return match


# GET
def get_match_from_id(session: Session, match_id: UUID) -> Match:
    match = read_from_db(
        Match,
        where=Match.id == match_id,
        unique=True,
        session=session,
    )
    return match


def get_all_matches(
    session: Session, as_df: bool = False
) -> list[Match] | pd.DataFrame:
    return read_from_db(Match, session=session, as_df=as_df)


def get_all_matches_from_league(
    session: Session, league_name: str, as_df: bool = False
) -> list[Match] | pd.DataFrame:
    return read_from_db(
        Match, where=Match.league_name == league_name, session=session, as_df=as_df
    )


# def get_last_matches(
#     session: Session, limit_last: int = 10, as_df: bool = False
# ) -> list[Match] | pd.DataFrame:
#     return read_from_db(Match, session=session, limit_last=limit_last, as_df=as_df)
#
#
# def get_all_matches_from_player(player: Player) -> list[Match]:
#     list_player_matches = player.matches
#     return list_player_matches
#
#
# def get_last_matches_from_player(player: Player, limit_last: int = 10) -> list[Match]:
#     list_player_matches = player.matches[:-limit_last]
#     return list_player_matches
#
#
# def get_all_matches_from_team(team: Team) -> list[Match]:
#     return team.matches
#
#
# def get_last_matches_from_team(team: Player, limit_last: int = 10) -> list[Match]:
#     return team.matches[:-limit_last]


def check_match_not_already_created(
    session: Session,
    teams: list[Team],
    league_name: str,
    date: datetime,
    score: str | MatchScore | None = None,
    logger: logging.Logger = LOGGER,
) -> None:
    """Raises MatchExistsError if already created, nothing otherwise"""
    list_matches_same_date_score = read_from_db(
        Match,
        session=session,
        where=(
            Match.date == date,
            Match.score == score,
            Match.league_name == league_name,
        ),
    )
    if list_matches_same_date_score:
        is_team1_in_match = False
        is_team2_in_match = False
        for match in list_matches_same_date_score:
            # Checks if teams in
            if teams[0] in match.teams:
                is_team1_in_match = True
            if teams[1] in match.teams:
                is_team2_in_match = True
            if is_team1_in_match and is_team2_in_match:
                err_msg = f"match ({teams[0]} vs {teams[1]}, {date=}) in {league_name=} already exists"
                logger.error(err_msg)
                raise MatchExistsError(err_msg)


# DELETE
def delete_match(session: Session, match_id: UUID | str) -> None:
    """Delete match after removing history.elo_gain corresponding to this match from players/team current elo
    Also updates league nb_matches.
    """
    if isinstance(match_id, str):
        match_id = UUID(match_id)

    # Retrieve match
    match = get_match_from_id(match_id=match_id, session=session)
    league = match.league

    # Update players and teams
    ## Manage players (Revert Elo gain from players from this match)
    match_elo_rating_history = read_from_db(
        EloRatingHistory, where=EloRatingHistory.match_id == match_id, session=session
    )
    list_players = []
    for row in match_elo_rating_history:
        player = row.player
        elo_rating_gain = row.elo_rating_gain
        player.elo_rating -= elo_rating_gain
        player.nb_matches -= 1
        if elo_rating_gain >= 0:
            player.nb_victories -= 1
        else:
            player.nb_defeats -= 1
        list_players.append(player)
    ## Manage teams (Revert Elo gain from players from this match)
    match_team_elo_rating_history = read_from_db(
        TeamEloRatingHistory,
        where=TeamEloRatingHistory.match_id == match_id,
        session=session,
    )
    list_teams = []
    for row in match_team_elo_rating_history:
        team = row.team
        elo_rating_gain = row.elo_rating_gain
        team.elo_rating -= elo_rating_gain
        team.nb_matches -= 1
        if elo_rating_gain > 0:
            team.nb_victories -= 1
        else:
            team.nb_defeats -= 1
        list_teams.append(team)
    ## Manage league
    league.nb_matches -= 1
    ## Commit updates
    commit_to_db(*list_players, *list_teams, league, session=session)
    ranking_manager.update_players_rank(session=session, league=league)
    ## Delete history rows
    delete_from_db(
        *match_elo_rating_history, *match_team_elo_rating_history, session=session
    )

    # Finally delete
    delete_from_db(match, session=session)
    LOGGER.notif(f"deleted {match_id=} successfully")
