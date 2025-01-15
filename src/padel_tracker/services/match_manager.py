from uuid import UUID
from datetime import datetime

from pydantic import validate_call

from padel_tracker.models.players import Player
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.database.db import Session, get_db_session, commit_to_db, read_from_db, delete_from_db
from padel_tracker.services.ranking_manager import update_players_results_after_finished_match, update_players_rank


# TODO : CRUD Match

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

    # Revert Elo gain from players from this match

    # Finally delete
    delete_from_db(match, session=session)

#
# class MatchManager:
#     matches: list[Match] = []
#
#     @staticmethod
#     def append_match(match: Match) -> None:
#         MatchManager.matches.append(match)
#
#     @staticmethod
#     def create_match(
#         team1: tuple[Player, Player], team2: tuple[Player, Player],
#         date: datetime, score: MatchScore = None
#     ) -> Match:
#         """
#         Crée un nouveau match et l'ajoute à l'historique.
#         """
#         match = Match(team1=team1, team2=team2, date=date, score=score)
#         MatchManager.append_match(match)
#         return match
#
#     @staticmethod
#     def process_finished_match(match: Match) -> None:
#         """
#         Update players data based on match result
#         """
#         # Update Elo ratings
#         RankingManager.update_players_data(match)
#
#         # TODO: Refresh ranks accross full db
#
#     @staticmethod
#     def create_finished_match(
#         team1: tuple[Player, Player], team2: tuple[Player, Player], date: datetime, score: MatchScore
#     ) -> Match:
#         """
#         Creates and process
#         """
#         match = MatchManager.create_match(
#             team1=team1, team2=team2, date=date, score=score
#         )
#         MatchManager.process_finished_match(match)
#
#     @staticmethod
#     def get_match_history() -> list[Match]:
#         """
#         Retourne l'historique des matchs.
#         """
#         return MatchManager.matches
