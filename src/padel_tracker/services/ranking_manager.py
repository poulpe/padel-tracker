from uuid import UUID

from padel_tracker.models.players import Player, EloRatingHistory, RankHistory, Team, TeamEloRatingHistory
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.models.ranking import calc_player_elo_rating_gain, calc_k_value
from padel_tracker.database.db import commit_to_db, read_from_db, get_db_session


def update_players_results_after_finished_match(
    finished_match_id: UUID,
    # db_session:Session=None,
    # close_session:bool=False
) -> dict[UUID, int]:
    """Update for each players:
    - Elo ratings, Elo k
    - Nb matches played, nb victories, nb defeats
    - Best Elo
    - Elo history

    Returns
    -------
    dict_elo_rating_gains:dict[UUID, int]
        Elo gains for convenience, as dict[player.id, elo_rating_gain]
    """
    with get_db_session() as session:
        # Retrieve Match
        finished_match: Match = read_from_db(
            Match,
            where=Match.id == finished_match_id,
            unique=True,
            session=session,
            close_session=False,
        )
        finished_match.post_init() # To write match name + validate players OK
        winner_team, loser_team = finished_match.get_winners_losers()
        winners = winner_team.players
        losers = loser_team.players

        # Get once all current Elo
        current_elo_rating_winner_player1 = winners[0].elo_rating #winners[0].elo_rating
        current_elo_rating_winner_player2 = winners[1].elo_rating #winners[1].elo_rating
        current_elo_rating_loser_player1  = losers[0].elo_rating #losers[0].elo_rating
        current_elo_rating_loser_player2  = losers[1].elo_rating #losers[1].elo_rating
        match_score = MatchScore.from_string(finished_match.score)
        nb_won_sets_diff = match_score.nb_won_sets_diff
        nb_won_games_diff = match_score.nb_won_games_diff

        # Calc all new (careful not updating yet Elo, for not screwing in btw calc)
        dict_elo_rating_gains = {}

        dict_elo_rating_gains[winners[0].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_winner_player1,
            teammate_elo_rating=current_elo_rating_winner_player2,
            opponent_player1_elo_rating=current_elo_rating_loser_player1,
            opponent_player2_elo_rating=current_elo_rating_loser_player2,
            player_nb_matches=winners[0].nb_matches,
            has_won=True,
            diff_nb_sets=nb_won_sets_diff,
            diff_nb_games=nb_won_games_diff,
        )
        dict_elo_rating_gains[winners[1].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_winner_player2,
            teammate_elo_rating=current_elo_rating_winner_player1,
            opponent_player1_elo_rating=current_elo_rating_loser_player1,
            opponent_player2_elo_rating=current_elo_rating_loser_player2,
            player_nb_matches=winners[1].nb_matches,
            has_won=True,
            diff_nb_sets=nb_won_sets_diff,
            diff_nb_games=nb_won_games_diff,
        )
        dict_elo_rating_gains[losers[0].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_loser_player1,
            teammate_elo_rating=current_elo_rating_loser_player2,
            opponent_player1_elo_rating=current_elo_rating_winner_player1,
            opponent_player2_elo_rating=current_elo_rating_winner_player2,
            player_nb_matches=losers[0].nb_matches,
            has_won=False,
            diff_nb_sets=nb_won_sets_diff,
            diff_nb_games=nb_won_games_diff,
        )
        dict_elo_rating_gains[losers[1].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_loser_player2,
            teammate_elo_rating=current_elo_rating_loser_player1,
            opponent_player1_elo_rating=current_elo_rating_winner_player1,
            opponent_player2_elo_rating=current_elo_rating_winner_player2,
            player_nb_matches=losers[1].nb_matches,
            has_won=False,
            diff_nb_sets=nb_won_sets_diff,
            diff_nb_games=nb_won_games_diff,
        )

        # Update players elo ratings, best Elo, nb_matches, elo k
        elo_history_entries = []
        for player in winners+losers:
            # Update player updated_date
            player.update_last_match_date()
            # Updated Elo
            elo_rating_gain = dict_elo_rating_gains[player.id]
            updated_elo_rating = player.elo_rating + elo_rating_gain
            player.elo_rating = updated_elo_rating
            # Best Elo
            if updated_elo_rating > player.best_elo_rating:
                player.best_elo_rating = updated_elo_rating
            # Nb matches
            player.nb_matches += 1
            # New k Elo
            player.elo_k = calc_k_value(player.nb_matches)
            # Update EloHistory (elo history only)
            player_elo_history_entry = EloRatingHistory(
                date=finished_match.date,
                player_id=player.id,
                player_name=player.name,
                elo_rating=updated_elo_rating,
                elo_rating_gain=elo_rating_gain,
            )
            elo_history_entries.append(player_elo_history_entry)
        # Update nb victory/defeat
        for player in winners:
            player.nb_victories += 1
        for player in losers:
            player.nb_defeats += 1

        # Update db
        commit_to_db(
            *winners,
            *losers,
            *elo_history_entries,
            finished_match,
            session=session,
            close_session=False,
        )

    return dict_elo_rating_gains


#TODO : update_teams_results_after_finished_match
def update_teams_results_after_finished_match(
    finished_match_id: UUID,
    # db_session:Session=None,
    # close_session:bool=False
) -> dict[UUID, int]:
    """Update for each teams, after calculation of each players:
    - Elo ratings
    - Nb matches played, nb victories, nb defeats
    - Best Elo
    - Team Elo rating history

    Returns
    -------
    dict_elo_rating_gains:dict[UUID, int]
        Elo gains for convenience, as dict[team.id, elo_rating_gain]
    """
    with get_db_session() as session:
        # Retrieve Match
        finished_match: Match = read_from_db(
            Match,
            where=Match.id == finished_match_id,
            unique=True,
            session=session,
            close_session=False,
        )
        finished_match.post_init() # To write match name + validate players OK
        winner_team, loser_team = finished_match.get_winners_losers()

        team_elo_history_entries = []
        dict_team_elo_rating_gains = {}
        for team in [winner_team, loser_team]:
            team.update_last_match_date()
            # Update Team elo (will trigger comput of self.elo_rating)
            previous_elo_rating = team.elo_rating
            updated_elo_rating = team.calc_team_elo_rating()
            elo_rating_gain = updated_elo_rating - previous_elo_rating
            dict_team_elo_rating_gains[team.id] = elo_rating_gain
            # Best Elo
            if updated_elo_rating > team.best_elo_rating:
                team.best_elo_rating = updated_elo_rating
            # Nb matches
            team.nb_matches += 1
            team_elo_history_entry = TeamEloRatingHistory(
                date=finished_match.date,
                team_id=team.id,
                team_name=team.name,
                elo_rating=updated_elo_rating,
                elo_rating_gain=elo_rating_gain,
            )
            team_elo_history_entries.append(team_elo_history_entry)

        # Update nb victory/defeat
        winner_team.nb_victories += 1
        loser_team.nb_defeats += 1

        # Update db
        commit_to_db(
            winner_team,
            loser_team,
            *team_elo_history_entries,
            finished_match,
            session=session,
            close_session=False,
        )

    return dict_team_elo_rating_gains

def update_players_rank() -> None:
    """Calc ranks and updated database"""
    with get_db_session() as session:
        # Get all players, sorted by top Elo to bottom Elo (descending order)
        sorted_players = read_from_db(
            Player, order_by=Player.elo_rating, order_descending=True
        )
        # Update players
        rank_history_entries = []
        for rank, player in enumerate(sorted_players, start=1):
            # Update rank
            player.rank = rank
            # Update best rank
            if (player.best_rank is None) or (player.best_rank > rank):
                player.best_rank = rank
            # Update RankHistory (date will be auto fulfilled as "now" if not provided)
            rank_history_entry = RankHistory(
                player_id=player.id,
                player_name=player.name,
                rank=rank,
            )
            rank_history_entries.append(rank_history_entry)
        commit_to_db(
            *sorted_players, *rank_history_entries, session=session, close_session=False
        )
