"""
CRUD on Matches and repercussions on players/teams

'session' refers as "database session", that can be obtained via call to get_db_session()
"""

import logging
from uuid import UUID
from datetime import datetime
from concurrent.futures.thread import ThreadPoolExecutor

import pandas as pd

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import (
    MatchExistsError,
    MatchNotFinishedError,
    SamePlayerInBothTeamsError,
)
from padel_tracker.models.leagues import League
from padel_tracker.models.players import Team, EloRatingHistory, TeamEloRatingHistory
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.services.common import check_players_all_in_league
from padel_tracker.services import ranking_manager

LOGGER = get_logger("matches")


def process_finished_match(
    session: Session,
    match: Match,
    is_update_elo: bool = True,
    delete_on_error: bool = True,
    thread_pool: ThreadPoolExecutor = None,
) -> tuple[dict[str, int], dict[str, int]]:
    try:
        dict_elo_rating_gains, dict_updated_elo_ratings = (
            ranking_manager.update_players_results_after_finished_match(
                session=session,
                match=match,
                is_update_elo=is_update_elo,
            )
        )
    except Exception:
        err_msg = "match is not finished: won't process"
        if delete_on_error:
            delete_from_db(match, session=session)
            err_msg += " and deleted it from db"
        LOGGER.error(err_msg)
        raise MatchNotFinishedError(err_msg)
    else:
        LOGGER.debug("starting update of league")
        league = match.league
        league.nb_matches += 1
        if not league.last_match_date or (league.last_match_date < match.date):
            league.last_match_date = match.date
        commit_to_db(league, session=session)
        LOGGER.info(f"league '{league.name}' has been updated from match id={match.id}")
        LOGGER.notif(f"processed finished_match id={match.id}")
    # Update_players_rank in a thread
    if is_update_elo:
        if thread_pool:
            thread_pool.submit(
                ranking_manager.update_players_rank,
                league_name=match.league.name,
                league_id=match.league.id,
                session=session,
            )
        else:
            ranking_manager.update_players_rank(
                league_name=match.league.name,
                league_id=match.league.id,
                session=session,
            )
    return dict_elo_rating_gains, dict_updated_elo_ratings


# CREATE


def create_match(
    session: Session,
    teams: list[Team],
    league_name: str,
    date: datetime,
    score: str | MatchScore | None = None,
    is_finished: bool = True,
    is_update_elo: bool = True,
) -> Match:
    """If score is not given, match will not be considered finished"""
    logger = LOGGER.getChild("create")

    # Normalize score as str for creation
    if isinstance(score, MatchScore):
        score = str(score)
    # Basic check nb teams
    logger.debug("performing basic checks")
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
    logger.debug("fetching league")
    league = read_from_db(
        League, where=League.name == league_name, session=session, unique=True
    )

    # Check match doesn't exist already
    logger.debug("checking match doesn't exist")
    check_match_not_already_created(
        session=session,
        teams=teams,
        date=date,
        league_name=league_name,
        logger=logger,
    )
    # Check players all in the same league
    players = [
        teams[0].players[0],
        teams[0].players[1],
        teams[1].players[0],
        teams[1].players[1],
    ]
    logger.debug("checking all players in league")
    check_players_all_in_league(players=players, league=league)

    # Create match
    logger.debug("creating match")
    match = Match(
        teams=teams,
        team1_name=teams[0].name,
        team2_name=teams[1].name,
        players=players,
        date=date,
        score=score,
        league=league,
    )
    match.post_init()
    ## Commit
    logger.debug("committing to db")
    commit_to_db(match, league, session=session)
    logger.notif(
        f"created new Match({match} date='{match.date.strftime("%d/%m/%Y %H:%M")}')"
    )
    # Process it if finished
    if is_finished:
        process_finished_match(
            session=session, match=match, is_update_elo=is_update_elo
        )
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


def check_match_not_already_created(
    session: Session,
    teams: list[Team],
    league_name: str,
    date: datetime,
    logger: logging.Logger = LOGGER,
) -> None:
    """Raises MatchExistsError if already created, nothing otherwise

    Notes
    -----
    Score is not included in the search : isOK
        because a match with the same team + same date cannot exist physically...
    """
    list_matches_same_date = read_from_db(
        Match,
        session=session,
        where=(Match.date == date, Match.league_name == league_name),
    )
    if list_matches_same_date:
        for match in list_matches_same_date:
            if (teams[0] in match.teams) and (teams[1] in match.teams):
                err_msg = f"match ({teams[0]} vs {teams[1]}, {date=}) in {league_name=} already exists"
                logger.error(err_msg)
                raise MatchExistsError(err_msg)


# DELETE
def delete_match(
    session: Session,
    match_id: UUID | str,
    thread_pool: ThreadPoolExecutor = None,
) -> None:
    """Delete match after removing history.elo_gain corresponding to this match from players/team current elo
    Also updates league nb_matches.
    """
    logger = LOGGER.getChild("delete")

    if isinstance(match_id, str):
        match_id = UUID(match_id)

    # Retrieve match
    match = get_match_from_id(match_id=match_id, session=session)
    league = match.league

    # Update players and teams
    ## Manage players (Revert Elo gain from players from this match)
    #TODO (prio 1): check when a match was "friendly" and doesn't have any elo history
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
        ### Manage player last_match_date if applicable
        if match.date == player.last_match_date:
            # Find "before the last" match date
            try:
                sorted_matches = sorted(player.matches, key=lambda match: match.date)
                player.last_match_date = sorted_matches[-2].date
            except (KeyError, AttributeError, Exception):
                player.last_match_date = None
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
        ### Manage team last_match_date if applicable
        if match.date == team.last_match_date:
            # Find "before the last" match date
            try:
                sorted_matches = sorted(team.matches, key=lambda match: match.date)
                team.last_match_date = sorted_matches[-2].date
            except (KeyError, AttributeError, Exception):
                team.last_match_date = None
        list_teams.append(team)
    ## Manage league
    league.nb_matches -= 1
    ## Commit updates
    commit_to_db(*list_players, *list_teams, league, session=session)
    ## Delete history rows
    delete_from_db(
        *match_elo_rating_history, *match_team_elo_rating_history, session=session
    )
    # Finally delete
    delete_from_db(match, session=session)
    logger.notif(f"deleted {match_id=} successfully")
    # Update ranks in a thread (non blocking)
    if thread_pool:
        thread_pool.submit(
            ranking_manager.update_players_rank,
            league_name=league.name,
            league_id=league.id,
            session=session,
        )
    else:
        ranking_manager.update_players_rank(
            league_name=league.name,
            league_id=league.id,
            session=session,
        )
