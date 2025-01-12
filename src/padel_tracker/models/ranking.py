"""
Notes
-----
- Elo "rating" (R) is the final rank
- Elo "score" (E) is the expected "probability" vs an opponent (so f(self, opponent))
"""

import numpy as np

ELO_BASE_RATING = 1000
ELO_RATIO_RATING = 400

ELO_BASE_K = 50  # Base value for K
ELO_RATIO_K = 100  # Number of games to play for stabilizing Elo score


def calc_player_expected_elo_score(
    player_elo_rating: int, opponent1_elo_rating: int, opponent2_elo_rating: int
) -> float:
    # fmt: off
    player_expected_score = (
        1/(1+np.pow(10, (opponent1_elo_rating - player_elo_rating) / ELO_RATIO_RATING))
        + 1/(1+np.pow(10, (opponent2_elo_rating - player_elo_rating) / ELO_RATIO_RATING))
    ) / 2
    # fmt: on
    return player_expected_score


def calc_team_elo_rating(player_elo_rating: int, teammate_elo_rating: int) -> int:
    """Average of both elo ratings"""
    return int((player_elo_rating + teammate_elo_rating) / 2)


def calc_team_expected_elo_score(
    team_elo_rating: int,
    opponent_elo_rating: int,
) -> float:
    """As team"""
    return 1 / (
        1 + np.pow(10, (opponent_elo_rating - team_elo_rating) / ELO_RATIO_RATING)
    )


def calc_k_value(nb_matches: int) -> float:
    """Calc factor for adjusting vs number of matches / XP / representativity of current Elo"""
    return ELO_BASE_K / (1 + nb_matches / ELO_RATIO_K)


def calc_point_value(diff_nb_sets: int) -> float:
    """Calc factor for adjusting vs score difference"""
    # return 1 + (1.5**(2*diff_nb_games)/10)
    return 2 + ((np.log10(1 + abs(diff_nb_sets))) ** 3)


def calc_updated_player_elo_rating(
    player_elo_rating: int,
    teammate_elo_rating: int,
    opponent_player1_elo_rating: int,
    opponent_player2_elo_rating: int,
    player_nb_matches: int,
    has_won: bool,
    diff_nb_games: int,
) -> int:
    # Get teams Elo rating
    team_elo_rating = calc_team_elo_rating(player_elo_rating, teammate_elo_rating)
    opponent_elo_rating = calc_team_elo_rating(
        opponent_player1_elo_rating, opponent_player2_elo_rating
    )
    # Get teams expected score
    team_expected_elo_score = calc_team_expected_elo_score(
        team_elo_rating, opponent_elo_rating
    )

    win_factor = 1 if has_won else 0
    k = calc_k_value(player_nb_matches)
    point_factor = calc_point_value(diff_nb_games)
    elo_rating_gain = k * point_factor * (win_factor - team_expected_elo_score)
    updated_player_elo = int(player_elo_rating + elo_rating_gain)
    return updated_player_elo
