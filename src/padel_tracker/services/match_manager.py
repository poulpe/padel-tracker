"""
CRUD on Matches and repercussions on players/teams
"""

from uuid import UUID
from datetime import datetime

from pydantic import validate_call

from padel_tracker.models.players import Player
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.database.db import Session, get_db_session, commit_to_db, read_from_db, delete_from_db
from padel_tracker.services.ranking_manager import update_players_results_after_finished_match, update_players_rank


def process_finished_match(finished_match_id: UUID) -> None:
    update_players_results_after_finished_match(finished_match_id=finished_match_id)
    update_players_rank()

@validate_call
def create_finished_match(
    players:list[Player],
    date:datetime,
    score:str|MatchScore,
    session: Session,
) -> Match:
    if isinstance(score, MatchScore):
        score = str(score)
    match = Match(players=players, date=date, score=score)
    match_id = match.id
    # Commit
    commit_to_db(match, session=session)
    # Process
    process_finished_match(match_id)
    return match

@validate_call
def create_unfinished_match(
    players:list[Player],
    date:datetime,
    session: Session,
    score:str|MatchScore|None = None,
) -> Match:
    if isinstance(score, MatchScore):
        score = str(score)
    match = Match(players=players, date=date, score=score)
    # Commit
    commit_to_db(match, session=session)
    return match

@validate_call
def get_match_from_id(match_id:UUID, session: Session | None = None) -> Match:
    match = read_from_db(
        Match,
        where=Match.id == match_id,
        unique=True,
        session=session,
    )
    return match

#TODO : delete_match, mucho work to cascade_delete + revert correct Elo
# (idea: remove history.elo_gain corresponding to this match from players current elo?)
@validate_call
def delete_match(match_id:UUID, session: Session | None = None)->None:
    # Retrieve match
    match = get_match_from_id(match_id=match_id, session=session)

    # TODO: Revert Elo gain from players from this match

    # Finally delete
    delete_from_db(match, session=session)
