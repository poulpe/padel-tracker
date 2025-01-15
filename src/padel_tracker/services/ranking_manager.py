from uuid import UUID

from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.models.ranking import calc_player_elo_rating_gain, calc_k_value
from padel_tracker.database.db import commit_to_db, read_from_db, get_db_session

def update_players_results(
    finished_match_id: UUID,
    #db_session:Session=None,
    #close_session:bool=False
) -> dict[UUID, int]:
    """Update for each players
    - Elo ratings
    - Elo k
    - Nb matches played, nb victories, nb defeats
    - Best Elo
    - Elo history ?

    Returns
    -------
    dict_elo_rating_gains:dict[UUID, int]
        Elo gains for convenience, as dict[player.id, elo_rating_gain]
    """
    with get_db_session() as session:
        # Retrieve Match
        finished_match:Match = read_from_db(
            Match,
            where=Match.id==finished_match_id,
            unique=True,
            session=session,
            close_session=False,
        )
        winners, losers = finished_match.get_winners_losers()

        # Get once all current Elo
        current_elo_rating_winner_player1 = winners[0].elo_rating
        current_elo_rating_winner_player2 = winners[1].elo_rating
        current_elo_rating_loser_player1 = losers[0].elo_rating
        current_elo_rating_loser_player2 = losers[1].elo_rating
        match_score = MatchScore.from_string(finished_match.score)
        nb_won_sets_diff = match_score.nb_won_sets_diff

        # Calc all new (careful not updating yet Elo, for not screwing in btw calc)
        dict_elo_rating_gains = {}

        dict_elo_rating_gains[winners[0].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_winner_player1,
            teammate_elo_rating=current_elo_rating_winner_player2,
            opponent_player1_elo_rating=current_elo_rating_loser_player1,
            opponent_player2_elo_rating=current_elo_rating_loser_player2,
            player_nb_matches=winners[0].nb_matches,
            has_won=True,
            diff_nb_games=nb_won_sets_diff,
        )
        dict_elo_rating_gains[winners[1].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_winner_player2,
            teammate_elo_rating=current_elo_rating_winner_player1,
            opponent_player1_elo_rating=current_elo_rating_loser_player1,
            opponent_player2_elo_rating=current_elo_rating_loser_player2,
            player_nb_matches=winners[1].nb_matches,
            has_won=True,
            diff_nb_games=nb_won_sets_diff,
        )
        dict_elo_rating_gains[losers[0].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_loser_player1,
            teammate_elo_rating=current_elo_rating_loser_player2,
            opponent_player1_elo_rating=current_elo_rating_winner_player1,
            opponent_player2_elo_rating=current_elo_rating_winner_player2,
            player_nb_matches=losers[0].nb_matches,
            has_won=False,
            diff_nb_games=nb_won_sets_diff,
        )
        dict_elo_rating_gains[losers[1].id] = calc_player_elo_rating_gain(
            player_elo_rating=current_elo_rating_loser_player2,
            teammate_elo_rating=current_elo_rating_loser_player1,
            opponent_player1_elo_rating=current_elo_rating_winner_player1,
            opponent_player2_elo_rating=current_elo_rating_winner_player2,
            player_nb_matches=losers[1].nb_matches,
            has_won=False,
            diff_nb_games=nb_won_sets_diff,
        )

        # Update players elo ratings, best Elo, nb_matches, elo k
        for player in winners + losers:
            # Updated Elo
            updated_elo_rating = player.elo_rating + dict_elo_rating_gains[player.id]
            player.elo_rating = updated_elo_rating
            # Best Elo
            if updated_elo_rating > player.best_elo_rating:
                player.best_elo_rating = updated_elo_rating
            # Nb matches
            player.nb_matches += 1
            # New k Elo
            player.elo_k = calc_k_value(player.nb_matches)
            # #TODO: Update Elo history
            # if player.elo_rating_history is None:
            #     player.init_elo_rating_history()
            # player.elo_rating_history[finished_match.date] = updated_elo_rating

        # Update nb victory/defeat
        for player in winners:
            player.nb_victories += 1
        for player in losers:
            player.nb_defeats += 1

        # Update db
        commit_to_db(*winners, *losers, finished_match, session=session, close_session=False)

    return dict_elo_rating_gains