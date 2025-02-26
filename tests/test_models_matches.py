from padel_tracker.models.players import Player, Team
from padel_tracker.models.matches import Match, MatchScore


def test_create_match():
    p1 = Player(name="player one", elo_rating=1000)
    p2 = Player(name="player two", elo_rating=1000)
    p3 = Player(name="player three", elo_rating=1200)
    p4 = Player(name="player four", elo_rating=1300)

    t1 = Team(players=[p1, p2])
    t2 = Team(players=[p3, p4])
    t1.post_init()
    t2.post_init()

    score = MatchScore(
        games_set1_team1=7,
        games_set1_team2=5,
        games_set2_team1=6,
        games_set2_team2=3,
        # games_set1_team1=7,
        # games_set1_team2=5,
    )
    assert str(score) == "7-5, 6-3"

    match1 = Match(
        teams=[t1, t2], players=[p1, p2, p3, p4], team1_name=t1.name, team2_name=t2.name,
    )
    match1.score = str(score)
    winners, losers = match1.get_winners_losers()
    assert winners == t1
    assert losers == t2


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
