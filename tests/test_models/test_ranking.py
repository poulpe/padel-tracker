from padel_tracker.models.ranking import (
    calc_player_expected_elo_score,
    calc_team_elo_rating,
    calc_team_expected_elo_score,
    calc_k_value,
    calc_points_factor,
    calc_player_elo_rating_gain,
)


def test_calc_player_expected_elo_score():
    expected = calc_player_expected_elo_score(1200, 1300, 1100)
    assert 0 <= expected <= 1


def test_calc_team_elo_rating():
    assert calc_team_elo_rating(1200, 1300) == 1250


def test_calc_team_expected_elo_score():
    expected = calc_team_expected_elo_score(840, 1300)
    assert 0 <= expected <= 1


def test_calc_k_value():
    assert calc_k_value(0) > calc_k_value(50)


def test_calc_points_factor():
    assert calc_points_factor(2, 10) > 1


def test_calc_player_elo_rating_gain():
    elo_gain = calc_player_elo_rating_gain(
        player_elo_rating=1200,
        teammate_elo_rating=1050,
        opponent_player1_elo_rating=1230,
        opponent_player2_elo_rating=1150,
        player_nb_matches=26,
        has_won=False,
        diff_nb_sets=1,
        diff_nb_games=5,
    )
    assert isinstance(elo_gain, int)
    assert elo_gain < 0
