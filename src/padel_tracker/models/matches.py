from typing import Self
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, NonNegativeInt

from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.links import PlayerMatchLink #, PlayerTeamLink, TeamMatchLink
from padel_tracker.models.players import Player #, Team

############ Match ############

class MatchScore(BaseModel, validate_assignment=True):
    games_set1_team1: NonNegativeInt = Field(0, le=7)
    games_set1_team2: NonNegativeInt = Field(0, le=7)
    games_set2_team1: NonNegativeInt | None = Field(None, le=7)
    games_set2_team2: NonNegativeInt | None = Field(None, le=7)
    games_set3_team1: NonNegativeInt | None = Field(None, le=10)
    games_set3_team2: NonNegativeInt | None = Field(None, le=10)
    nb_played_sets: NonNegativeInt = Field(0, le=3)
    nb_won_sets_team1: NonNegativeInt = Field(0, le=3)
    nb_won_sets_team2: NonNegativeInt = Field(0, le=3)
    nb_won_sets_diff: NonNegativeInt = Field(0, le=3)
    won_sets: tuple[NonNegativeInt, NonNegativeInt] | None = Field(None)

    def check_basic_validity(self) -> None:
        """Checks games of both teams are given for a set and get number of played sets

        Raises
        ------
        ValueError
            If not games of both team in one set
        """
        # Check Set#1
        self.nb_played_sets = 1
        if self.games_set1_team1 is None or self.games_set1_team2 is None:
            raise ValueError("Games must be given for both teams in Set#1")

        # Check Set#2
        if self.games_set2_team1 is not None and self.games_set2_team2 is not None:
            self.nb_played_sets = 2
        elif (self.games_set2_team1 is None and self.games_set2_team2 is not None) or (
            self.games_set2_team1 is not None and self.games_set2_team2 is None
        ):
            raise ValueError("Games must be given for both teams in Set#2")

        # Check Set#3
        if self.games_set3_team1 is not None and self.games_set3_team2 is not None:
            self.nb_played_sets = 3
        elif (self.games_set3_team1 is None and self.games_set3_team2 is not None) or (
            self.games_set3_team1 is not None and self.games_set3_team2 is None
        ):
            raise ValueError("Games/Points must be given for both teams in Set#3")

    def check_set_validity(self, games_team1: int, games_team2: int) -> None:
        """Checks 2 games diff in a set or arrived to 7"""
        if (games_team1 == 6 or games_team2 == 6) and (
            abs(games_team2 - games_team1) >= 2
        ):
            pass
        elif (games_team1 >= 7 or games_team2 >= 7) and (
            abs(games_team2 - games_team1) >= 1
        ):
            pass
        else:
            raise ValueError(f"set is not valid. {games_team1=} and {games_team2=}")

    def check_final_validity(self) -> None:
        """Checks 2 games diff or arrived to 7 in each played set"""
        self.check_basic_validity()
        # Check Set #1
        self.check_set_validity(self.games_set1_team1, self.games_set1_team2)
        # Check Set#2
        if self.nb_played_sets >= 2:
            self.check_set_validity(self.games_set2_team1, self.games_set2_team2)
        # Check Set#3
        if self.nb_played_sets >= 3:
            self.check_set_validity(self.games_set3_team1, self.games_set3_team2)

    def calc_won_sets(self) -> tuple[int, int]:
        self.check_final_validity()
        self.nb_won_sets_team1 = 0
        self.nb_won_sets_team2 = 0
        # Check Set#1
        if self.games_set1_team1 > self.games_set1_team2:
            self.nb_won_sets_team1 += 1
        else:
            self.nb_won_sets_team2 += 1
        # Check Set#2
        if self.nb_played_sets >= 2:
            if self.games_set2_team1 > self.games_set2_team2:
                self.nb_won_sets_team1 += 1
            else:
                self.nb_won_sets_team2 += 1
        # Check Set#3
        if self.nb_played_sets >= 3:
            if self.games_set3_team1 > self.games_set3_team2:
                self.nb_won_sets_team1 += 1
            else:
                self.nb_won_sets_team2 += 1

        self.won_sets = (self.nb_won_sets_team1, self.nb_won_sets_team2)
        self.nb_won_sets_diff = abs(self.nb_won_sets_team1 - self.nb_won_sets_team2)
        return self.won_sets

    def __str__(self):
        self.check_basic_validity()
        score = f"{self.games_set1_team1}-{self.games_set1_team2}"
        if self.nb_played_sets >= 2:
            score += f", {self.games_set2_team1}-{self.games_set2_team2}"
        if self.nb_played_sets == 3:
            score += f", {self.games_set3_team1}-{self.games_set3_team2}"
        return score

    @classmethod
    def from_string(cls, score_string: str) -> Self:
        """Create a MatchScore object from string "comma-separated" formatted as i.e:
        "6-4, 3-6, 6-2"

        Examples
        --------
        >>> score = MatchScore.from_string("6-4, 3-6, 6-2")
        """
        list_sets = score_string.split(", ")

        list_games = []
        while len(list_sets) > 0:
            current_set = list_sets.pop(0)
            games_team1 = current_set.split("-")[0]
            list_games.append(games_team1)
            games_team2 = current_set.split("-")[1]
            list_games.append(games_team2)

        if len(list_games) == 4:
            list_games.append(None)
            list_games.append(None)

        match_score = MatchScore(
            games_set1_team1=list_games[0],
            games_set1_team2=list_games[1],
            games_set2_team1=list_games[2],
            games_set2_team2=list_games[3],
            games_set3_team1=list_games[4],
            games_set3_team2=list_games[5],
        )
        match_score.check_basic_validity()
        return match_score


#TODO (prio1) : should players be a list ? and then point out to teams after

# class Match(SQLModel, table=True, validate_assignment=True):
#     team1: tuple[Player, Player] = Relationship(back_populates="matches_history")
#     team2: tuple[Player, Player] = Relationship(back_populates="matches_history")
#     id: int | None = Field(None, primary_key=True)
#     date: datetime = Field(default_factory=now, description="Match execution date")
#     score:str|None = Field(None)
#     #score: MatchScore = Field(default_factory=MatchScore) #TODO : doubt, should be string ?
#     creation_date: datetime = Field(
#         default_factory=now, description="Creation of match in database"
#     )
#     winners: tuple[Player, Player] = Field(None)
#     losers: tuple[Player, Player] = Field(None)
#
#     def __setattr__(self, key, value):
#         # Ensure field is not "read-only"
#         frozen_fields = {"id", "creation_date"}
#         ensure_frozen_field(self, key, frozen_fields)
#         # Write assignment
#         super().__setattr__(key, value)
#
#     def get_winners(self) -> tuple[Player, Player]:
#         """"""
#         match_score = MatchScore.from_string(self.score)
#         match_score.calc_won_sets()
#         if match_score.nb_won_sets_team1 > match_score.nb_won_sets_team2:
#             self.winners = self.team1
#             self.losers = self.team2
#         elif match_score.nb_won_sets_team1 < match_score.nb_won_sets_team2:
#             self.winners = self.team2
#             self.losers = self.team1
#         else:
#             raise ValueError(f"no winner yet ({match_score = })")
#         return self.winners

class Match(SQLModel, table=True, validate_assignment=True):
    #teams:list[Team] = Relationship(back_populates="matches", link_model=TeamMatchLink)
    players: list[Player] = Relationship(back_populates="matches", link_model=PlayerMatchLink)
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    date: datetime = Field(default_factory=now, description="Match execution date")
    score:str|None = Field(None, description="Score as a string formatted '6-4, 7-5'")
    creation_date: datetime = Field(
        default_factory=now, description="Creation of match in database"
    )

    def validate_players(self):
        nb_players = len(self.players)
        if nb_players != 4:
            raise ValueError(f"a match must have exactly 4 players. Got {nb_players=}")

    def get_winners_losers(self) -> tuple[list[Player], list[Player]]:
        """"""
        self.validate_players()
        match_score = MatchScore.from_string(self.score)
        match_score.calc_won_sets()
        if match_score.nb_won_sets_team1 > match_score.nb_won_sets_team2:
            winners = [self.players[0], self.players[1]]
            losers = [self.players[2], self.players[3]]
        elif match_score.nb_won_sets_team1 < match_score.nb_won_sets_team2:
            losers = [self.players[0], self.players[1]]
            winners = [self.players[2], self.players[3]]
        else:
            raise ValueError(f"no winner yet ({match_score = })")
        return winners, losers

if __name__ == "__main__":
    p1 = Player(name="p1", elo_rating=1000)
    p2 = Player(name="p2", elo_rating=1000)
    p3 = Player(name="p3", elo_rating=1200)
    p4 = Player(name="p4", elo_rating=1300)

    # t1 = Team(players=[p1,p2])
    # t2 = Team(players=[p3,p4])

    score = MatchScore(
        games_set1_team1=7,
        games_set1_team2=5,
        games_set2_team1=6,
        games_set2_team2=3,
        # games_set1_team1=7,
        # games_set1_team2=5,
    )
    print(score)
    # print(str(score))
    # score = MatchScore()

    match1 = Match(
        players=[p1,p2,p3,p4],
        score=str(score),
        #teams=[t1,t2],
    )
    print(match1)
    winners, losers = match1.get_winners_losers()
    print(match1.get_winners_losers())
    #match1.score = score
    #winner = match1.get_winners()
    #print(winner)

    #score_from_str = MatchScore.from_string("6-4, 3-6, 6-2")
    #assert score_from_str.games_set2_team2 == 6
