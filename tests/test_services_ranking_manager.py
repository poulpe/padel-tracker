import datetime

from padel_tracker.models.players import Player
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.services.ranking_manager import update_players_results


def test_update_elo_ratings():
    p1 = Player(name="p1", elo_rating=1000)
    p2 = Player(name="p2", elo_rating=940, nb_matches=100)
    p3 = Player(name="p3", elo_rating=1200)
    p4 = Player(name="p4", elo_rating=1100, nb_matches=50)

    t1 = (p1, p2)
    t2 = (p3, p4)

    # score = MatchScore(
    #     games_set1_team1=7,
    #     games_set1_team2=5,
    #     games_set2_team1=6,
    #     games_set2_team2=3,
    #     # games_set3_team1=3,
    #     # games_set3_team2=6,
    # )
    score = MatchScore(
        games_set1_team2=7,
        games_set1_team1=5,
        games_set2_team2=6,
        games_set2_team1=3,
        # games_set3_team1=3,
        # games_set3_team2=6,
    )
    print(score)
    print(str(score))
    # score = MatchScore()

    match1 = Match(team1=t1, team2=t2, date=datetime.datetime.now())
    match1.score = score
    winner = match1.get_winners()
    print(winner)

    print(f"INIT {p1.elo_rating = }")
    print(f"INIT {p2.elo_rating = }")
    print(f"INIT {p3.elo_rating = }")
    print(f"INIT {p4.elo_rating = }")

    update_players_results(match1)

    print(f"UPDATED {p1.elo_rating = }")
    print(f"UPDATED {p2.elo_rating = }")
    print(f"UPDATED {p3.elo_rating = }")
    print(f"UPDATED {p4.elo_rating = }")
    print(p1)
