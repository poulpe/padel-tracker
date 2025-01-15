from uuid import UUID

# from datetime import datetime
#
# from padel_tracker.models.matches import Match, MatchScore
# from padel_tracker.models.players import Player
# from padel_tracker.services.ranking_manager import update_players_results


# TODO : CRUD Match
def create_match_to_db():
    pass


def process_finished_match(finished_match_id: UUID) -> None:
    pass


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
