from datetime import datetime, timedelta

from padel_tracker.models.players import Player, Team
from padel_tracker.models.matches import Match, MatchScore

from padel_tracker.services.match_manager import MatchManager


p1 = Player(name="p1", elo_rating=1000)
p2 = Player(name="p2", elo_rating=1000)
p3 = Player(name="p3", elo_rating=1200)
p4 = Player(name="p4", elo_rating=1300)

t1 = Team(player1=p1, player2=p2)
t2 = Team(player1=p3, player2=p4)

score = MatchScore(
    games_set1_team1=7,
    games_set1_team2=5,
    games_set2_team1=6,
    games_set2_team2=3,
    # games_set1_team1=7,
    # games_set1_team2=5,
)
# print(score)
# print(str(score))
# score = MatchScore()

# match1 = Match(team1=t1, team2=t2, date=datetime.datetime.now())
# match1.score = score
# winner = match1.get_winners()
# print(winner)

#

new_match = MatchManager.create_match(
    team1=t1, team2=t2, date=datetime.now() - timedelta(days=1), score=score
)
MatchManager.process_finished_match(new_match)
print(MatchManager.matches)
print(p2)

# Create Match 2
score2 = MatchScore(
    games_set1_team1=7,
    games_set1_team2=5,
    games_set2_team1=3,
    games_set2_team2=6,
    games_set3_team1=5,
    games_set3_team2=7,
)
MatchManager.process_finished_match(new_match)

print("finished")
