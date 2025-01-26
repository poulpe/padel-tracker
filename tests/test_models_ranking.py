# from padel_tracker.models.players import Player
from padel_tracker.models.ranking import (
    calc_points_factor,
)


def test_calculate_team_expected_score():
    # p1 = Player(name="p1", elo_rating=1000)
    # p2 = Player(name="p2", elo_rating=1000)
    # p3 = Player(name="p3", elo_rating=1200)
    # p4 = Player(name="p4", elo_rating=1300)

    # t1 = (p1, p2)
    # t2 = (p3, p4)

    # Et1 = calc_team_expected_elo_score(
    #     t1.player1.elo_rating,
    #     t1.player2.elo_rating,
    #     t2.player1.elo_rating,
    #     t2.player2.elo_rating,
    # )
    # Et2 = calc_team_expected_elo_score(
    #     t2.player1.elo_rating,
    #     t2.player2.elo_rating,
    #     t1.player1.elo_rating,
    #     t1.player2.elo_rating,
    # )

    # print(f"{Et1=}")
    # print(f"{Et2=}")
    #
    # Et1_yes = t1.calc_team_expected_elo_score(t2)
    # Et2_yes = t2.calc_team_expected_elo_score(t1)
    #
    # print(f"{Et1_yes=}")
    # print(f"{Et2_yes=}")
    pass


def test_calc_point_value():
    list_diff_nb_games = [i for i in range(1, 12 + 1)]
    list_diff_nb_sets = [1, 2]
    for diff_sets in list_diff_nb_sets:
        for diff_games in list_diff_nb_games:
            factor = calc_points_factor(
                diff_nb_sets=diff_sets, diff_nb_games=diff_games
            )
            print(f"{diff_sets=}, {diff_games=} : {factor}")
