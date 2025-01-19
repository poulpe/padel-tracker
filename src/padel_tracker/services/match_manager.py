"""
CRUD on Matches and repercussions on players/teams

'session' refers as "database session", that can be obtained via call to get_db_session()
"""

from uuid import UUID
from datetime import datetime

import pandas as pd

from padel_tracker.utils.logs import get_logger, LOG_LEVEL_NOTIF
from padel_tracker.models.players import Player, Team
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.services.ranking_manager import (
    update_players_results_after_finished_match,
    update_players_rank,
)

LOGGER = get_logger("match_manager")


class MatchExistsError(Exception):
    """Match already exists in database"""


class MatchNotFoundError(Exception):
    """Match not found and probably doesn't exist in database"""


def process_finished_match(session: Session, finished_match: Match) -> None:
    update_players_results_after_finished_match(
        session=session, finished_match=finished_match
    )
    update_players_rank(session=session)
    info_msg = f"processed finished_match id={finished_match.id}"
    LOGGER.log(LOG_LEVEL_NOTIF, info_msg)


# CREATE


def create_match(
    session: Session,
    teams: list[Team],
    date: datetime,
    score: str | MatchScore | None = None,
    is_finished: bool = True,
) -> Match:
    """If score is not given, match will not be considered finished"""
    logger = LOGGER.getChild("create_match")

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

    # Create match
    players = [
        teams[0].players[0],
        teams[0].players[1],
        teams[1].players[0],
        teams[1].players[1],
    ]
    ## Check match doesn't exist already
    check_match_not_already_created(
        session=session, teams=teams, date=date, score=score
    )

    match = Match(teams=teams, players=players, date=date, score=score)
    match.post_init()
    # Commit
    commit_to_db(match, session=session)
    match_id = match.id
    logger.log(LOG_LEVEL_NOTIF, f"created new match id={match_id}")
    # Process it if finished
    if is_finished:
        try:
            process_finished_match(session=session, finished_match=match)
        except:
            delete_from_db(match, session=session)
            logger.error("match is not finished, deleted it from db and won't process")
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


def get_last_matches(
    session: Session, limit_last: int = 10, as_df: bool = False
) -> list[Match] | pd.DataFrame:
    return read_from_db(Match, session=session, limit_last=limit_last, as_df=as_df)


def get_all_matches_from_player(player: Player) -> list[Match]:
    list_player_matches = player.matches
    return list_player_matches


def get_last_matches_from_player(player: Player, limit_last: int = 10) -> list[Match]:
    list_player_matches = player.matches[:-limit_last]
    return list_player_matches


def get_all_matches_from_team(team: Team) -> list[Match]:
    return team.matches


def get_last_matches_from_team(team: Player, limit_last: int = 10) -> list[Match]:
    return team.matches[:-limit_last]


def check_match_not_already_created(
    session: Session,
    teams: list[Team],
    # players:list[Player],
    date: datetime,
    score: str | MatchScore | None = None,
) -> None:
    list_matches_same_date_score = read_from_db(
        Match,
        session=session,
        where=(Match.date == date, Match.score == score),
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
                # TODO : err_msg and logs
                raise MatchExistsError


# DELETE
# TODO (prio 3): delete_match, mucho work to cascade_delete + revert correct Elo
# (idea: remove history.elo_gain corresponding to this match from players current elo?)
def delete_match(session: Session, match_id: UUID) -> None:
    # Retrieve match
    match = get_match_from_id(match_id=match_id, session=session)

    # Revert Elo gain from players from this match

    # Finally delete
    delete_from_db(match, session=session)
