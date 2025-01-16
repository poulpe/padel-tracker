"""
CRUD on Matches and repercussions on players/teams

'session' refers as "database session", that can be obtained via call to get_db_session()
"""

from uuid import UUID
from datetime import datetime

from padel_tracker.models.players import Team
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


def process_finished_match(session: Session, finished_match: Match) -> None:
    update_players_results_after_finished_match(
        session=session, finished_match=finished_match
    )
    update_players_rank(session=session)


def create_match(
    session: Session,
    teams: list[Team],
    date: datetime,
    score: str | MatchScore | None = None,
) -> Match:
    """If score is not given, match will not be considered finished"""
    # Normalize score as str for creation
    if isinstance(score, MatchScore):
        score = str(score)
    # Basic check nb teams
    nb_teams = len(teams)
    if nb_teams != 2:
        raise ValueError(f"a match must have exactly 2 teams. Got {nb_teams=}")
    for team in teams:
        nb_player = len(team.players)
        if nb_player != 2:
            err_msg = f"a team must have exactly 2 players. Got {nb_player=} in {team=}"
            raise ValueError(err_msg)
    # Create match
    players = [
        teams[0].players[0],
        teams[0].players[1],
        teams[1].players[0],
        teams[1].players[1],
    ]
    match = Match(teams=teams, players=players, date=date, score=score)
    match.post_init()
    # Commit
    commit_to_db(match, session=session)
    # Check if match is finished and process it if it's the case
    try:
        match.get_winners_losers()
    except ValueError:
        pass
    else:
        process_finished_match(session=session, finished_match=match)
    return match


def get_match_from_id(session: Session, match_id: UUID) -> Match:
    match = read_from_db(
        Match,
        where=Match.id == match_id,
        unique=True,
        session=session,
    )
    return match


# TODO : delete_match, mucho work to cascade_delete + revert correct Elo
# (idea: remove history.elo_gain corresponding to this match from players current elo?)
def delete_match(session: Session, match_id: UUID) -> None:
    # Retrieve match
    match = get_match_from_id(match_id=match_id, session=session)

    # TODO: Revert Elo gain from players from this match

    # Finally delete
    delete_from_db(match, session=session)
