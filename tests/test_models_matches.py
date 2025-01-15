import datetime

from padel_tracker.models.players import Player
from padel_tracker.models.matches import Match, MatchScore


def test_create_match_score():
    p1 = Player(name="p1", elo_rating=1000)
    p2 = Player(name="p2", elo_rating=1000)
    p3 = Player(name="p3", elo_rating=1200)
    p4 = Player(name="p4", elo_rating=1300)

    # t1 = Team(player1=p1, player2=p2)
    # t2 = Team(player1=p3, player2=p4)
    t1 = (p1, p2)
    t2 = (p3, p4)

    score = MatchScore(
        games_set1_team1=7,
        games_set1_team2=5,
        games_set2_team1=6,
        games_set2_team2=3,
        # games_set1_team1=7,
        # games_set1_team2=5,
    )
    print(score)
    print(str(score))
    # score = MatchScore()

    match1 = Match(team1=t1, team2=t2, date=datetime.datetime.now())
    match1.score = score
    winner = match1.get_winners()
    print(winner)


def test_create_match_score_from_string():
    # With 3 sets
    score_from_str = MatchScore.from_string("6-4, 3-6, 6-2")
    assert score_from_str.games_set2_team2 == 6
    score_from_class = MatchScore(
        games_set1_team1=6,
        games_set1_team2=4,
        games_set2_team1=3,
        games_set2_team2=6,
        games_set3_team1=6,
        games_set3_team2=2,
    )
    assert str(score_from_class) == str(score_from_str)

    # With 2 sets
    score_from_str = MatchScore.from_string("6-4, 6-1")
    assert score_from_str.games_set2_team2 == 1
    score_from_class = MatchScore(
        games_set1_team1=6,
        games_set1_team2=4,
        games_set2_team1=6,
        games_set2_team2=1,
    )
    assert str(score_from_class) == str(score_from_str)
