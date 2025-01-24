"""
Notes
-----
- Elo "rating" (R) is the final rank
- Elo "score" (E) is the expected "probability" vs an opponent (so f(self, opponent))
"""

ELO_BASE_RATING = 1000
ELO_RATIO_RATING = 400

ELO_BASE_K = 50  # Base value for K
ELO_RATIO_K = 100  # Number of games to play for stabilizing Elo score


def calc_player_expected_elo_score(
    player_elo_rating: int, opponent1_elo_rating: int, opponent2_elo_rating: int
) -> float:
    # fmt: off
    player_expected_score = (
          1 / (1+10**((opponent1_elo_rating - player_elo_rating) / ELO_RATIO_RATING))
        + 1 / (1+10**((opponent2_elo_rating - player_elo_rating) / ELO_RATIO_RATING))
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
    return 1 / (1 + 10 ** ((opponent_elo_rating - team_elo_rating) / ELO_RATIO_RATING))


def calc_k_value(nb_matches: int) -> float:
    """Calc factor for adjusting vs number of matches / XP / representativity of current Elo"""
    return ELO_BASE_K / (1 + nb_matches / ELO_RATIO_K)


def calc_points_factor(diff_nb_sets: int, diff_nb_games: int) -> float:
    """Calc factor for adjusting vs score difference"""
    # Games factor
    if diff_nb_games <= 1:
        games_factor_percent = 0
    elif diff_nb_games >= 12:
        games_factor_percent = 100
    else:
        games_factor_percent = 0.5 * diff_nb_games**2 + 2.5 * diff_nb_games - 6
    # Sets factor
    sets_factor_percent = 10 if diff_nb_sets >= 2 else 0
    return 1 + (games_factor_percent + sets_factor_percent) / 100


def calc_player_elo_rating_gain(
    player_elo_rating: int,
    teammate_elo_rating: int,
    opponent_player1_elo_rating: int,
    opponent_player2_elo_rating: int,
    player_nb_matches: int,
    has_won: bool,
    diff_nb_sets: int,
    diff_nb_games: int,
) -> int:
    """Calculate "gain" to add to get new elo rating of "player"

    Examples
    --------
    >>> my_elo_rating = 1200
    >>> elo_gain = calc_player_elo_rating_gain(
    ...     player_elo_rating=my_elo_rating,
    ...     teammate_elo_rating=1050,
    ...     opponent_player1_elo_rating=1230,
    ...     opponent_player2_elo_rating=1150,
    ...     player_nb_matches=26,
    ...     has_won=False,
    ...     diff_nb_sets=1,
    ...     diff_nb_games=5,
    ... )
    >>> elo_gain
    -34
    >>> my_elo_rating += elo_gain
    >>> my_elo_rating
    1166

    Returns
    -------
    elo_rating_gain:int
        Gain to add to player's Elo to get it updated
    """
    # Get teams Elo rating
    team_elo_rating = calc_team_elo_rating(player_elo_rating, teammate_elo_rating)
    opponent_elo_rating = calc_team_elo_rating(
        opponent_player1_elo_rating, opponent_player2_elo_rating
    )
    # Get teams expected score
    team_expected_elo_score = calc_team_expected_elo_score(
        team_elo_rating, opponent_elo_rating
    )
    # Finalized special factors
    win_factor = 1 if has_won else 0
    k = calc_k_value(player_nb_matches)
    point_factor = calc_points_factor(
        diff_nb_games=diff_nb_games, diff_nb_sets=diff_nb_sets
    )
    elo_rating_gain = int(2 * k * point_factor * (win_factor - team_expected_elo_score))
    return elo_rating_gain
