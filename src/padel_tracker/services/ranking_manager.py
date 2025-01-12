from padel_tracker.models.matches import Match
from padel_tracker.models.ranking import calc_updated_player_elo_rating, calc_k_value


class RankingManager:
    @staticmethod
    def update_players_data(finished_match: Match) -> None:
        """Update for each players
        - Elo ratings
        - Elo k
        - Nb matches played, nb victories, nb defeats
        - Best Elo
        """
        winner = finished_match.get_winner()
        loser = finished_match.loser

        # Get once all current Elo
        current_elo_rating_winner_player1 = winner.player1.elo_rating
        current_elo_rating_winner_player2 = winner.player2.elo_rating
        current_elo_rating_loser_player1 = loser.player1.elo_rating
        current_elo_rating_loser_player2 = loser.player2.elo_rating
        nb_won_sets_diff = finished_match.score.nb_won_sets_diff

        # Calc all new (careful not updating yet Elo, for not screwing in btw calc)
        dict_updated_elo_ratings = {}

        dict_updated_elo_ratings[winner.player1.id] = calc_updated_player_elo_rating(
            player_elo_rating=current_elo_rating_winner_player1,
            teammate_elo_rating=current_elo_rating_winner_player2,
            opponent_player1_elo_rating=current_elo_rating_loser_player1,
            opponent_player2_elo_rating=current_elo_rating_loser_player2,
            player_nb_matches=winner.player1.nb_matches,
            has_won=True,
            diff_nb_games=nb_won_sets_diff,
        )
        dict_updated_elo_ratings[winner.player2.id] = calc_updated_player_elo_rating(
            player_elo_rating=current_elo_rating_winner_player2,
            teammate_elo_rating=current_elo_rating_winner_player1,
            opponent_player1_elo_rating=current_elo_rating_loser_player1,
            opponent_player2_elo_rating=current_elo_rating_loser_player2,
            player_nb_matches=winner.player2.nb_matches,
            has_won=True,
            diff_nb_games=nb_won_sets_diff,
        )
        dict_updated_elo_ratings[loser.player1.id] = calc_updated_player_elo_rating(
            player_elo_rating=current_elo_rating_loser_player1,
            teammate_elo_rating=current_elo_rating_loser_player2,
            opponent_player1_elo_rating=current_elo_rating_winner_player1,
            opponent_player2_elo_rating=current_elo_rating_winner_player2,
            player_nb_matches=loser.player1.nb_matches,
            has_won=False,
            diff_nb_games=nb_won_sets_diff,
        )
        dict_updated_elo_ratings[loser.player2.id] = calc_updated_player_elo_rating(
            player_elo_rating=current_elo_rating_loser_player2,
            teammate_elo_rating=current_elo_rating_loser_player1,
            opponent_player1_elo_rating=current_elo_rating_winner_player1,
            opponent_player2_elo_rating=current_elo_rating_winner_player2,
            player_nb_matches=loser.player2.nb_matches,
            has_won=False,
            diff_nb_games=nb_won_sets_diff,
        )

        # Update players elo ratings, best Elo, nb_matches, elo k
        winners = [winner.player1, winner.player2]
        losers = [loser.player1, loser.player2]
        for player in winners + losers:
            # Updated Elo
            updated_elo_rating = dict_updated_elo_ratings[player.id]
            player.elo_rating = updated_elo_rating
            # Best Elo
            if updated_elo_rating > player.best_elo_rating:
                player.best_elo_rating = updated_elo_rating
            # Nb matches
            player.nb_matches += 1
            # New k Elo
            player.elo_k = calc_k_value(player.nb_matches)

        # Update nb victory/defeat
        for player in winners:
            player.nb_victories += 1
        for player in losers:
            player.nb_defeats += 1
