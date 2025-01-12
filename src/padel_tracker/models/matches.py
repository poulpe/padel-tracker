from typing import Self
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import NonNegativeInt
from sqlmodel import SQLModel, Field

from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.players import Team


class MatchScore(SQLModel, validate_assignment=True):
    games_set1_team1: NonNegativeInt = Field(0, le=7)
    games_set1_team2: NonNegativeInt = Field(0, le=7)
    games_set2_team1: NonNegativeInt = Field(None, le=7)
    games_set2_team2: NonNegativeInt = Field(None, le=7)
    games_set3_team1: NonNegativeInt = Field(None, le=10)
    games_set3_team2: NonNegativeInt = Field(None, le=10)
    nb_played_sets: NonNegativeInt = Field(0, le=3)
    nb_won_sets_team1: NonNegativeInt = Field(0, le=3)
    nb_won_sets_team2: NonNegativeInt = Field(0, le=3)
    nb_won_sets_diff: NonNegativeInt = Field(0, le=3)
    won_sets: tuple[NonNegativeInt, NonNegativeInt] = Field(None)

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

    @staticmethod
    def from_string(score_string: str) -> Self:
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


class Match(SQLModel, table=True, validate_assignment=True):
    team1: Team = Field(None)
    team2: Team = Field(None)
    date: datetime = Field(default_factory=now, description="Match execution date")
    score: MatchScore = Field(default_factory=MatchScore)
    id: UUID = Field(default_factory=uuid4)
    creation_date: datetime = Field(
        default_factory=now, description="Creation of match in database"
    )
    winner: Team = Field(None)
    loser: Team = Field(None)

    def __setattr__(self, key, value):
        # Ensure field is not "read-only"
        frozen_fields = {"id", "creation_date"}
        if key in frozen_fields:
            raise AttributeError(f"{key} is read-only, cannot be rewritten")
        # Write assignment
        super().__setattr__(key, value)

    def get_winner(self) -> Team:
        """"""
        self.score.calc_won_sets()
        if self.score.nb_won_sets_team1 > self.score.nb_won_sets_team2:
            self.winner = self.team1
            self.loser = self.team2
        elif self.score.nb_won_sets_team1 < self.score.nb_won_sets_team2:
            self.winner = self.team2
            self.loser = self.team1
        else:
            raise ValueError(f"no winner yet ({self.score = })")
        return self.winner
