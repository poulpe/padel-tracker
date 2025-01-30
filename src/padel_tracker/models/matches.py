from typing import Self
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, Column, DateTime
from pydantic import BaseModel, NonNegativeInt

from padel_tracker.utils.datetime_utils import now
from padel_tracker.utils.errors import MatchNotFinishedError
from padel_tracker.models.base import ValidatedSQLModel
from padel_tracker.models.links import LinkPlayerMatch, LinkTeamMatch
from padel_tracker.models.players import Player, Team


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
    nb_won_games_team1: NonNegativeInt = Field(0, le=28)
    nb_won_games_team2: NonNegativeInt = Field(0, le=28)
    nb_won_games_diff: NonNegativeInt = Field(0, le=16)
    won_sets: tuple[NonNegativeInt, NonNegativeInt] | None = Field(None)
    won_games: tuple[NonNegativeInt, NonNegativeInt] | None = Field(None)

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

    @classmethod
    def check_set_validity(self, games_team1: int, games_team2: int) -> None:
        """Checks 2 games diff in a set or arrived to 7"""
        games_diff = abs(games_team2 - games_team1)
        if ((games_team1 == 6) != (games_team2 == 6)) and (games_diff >= 2):
            pass
        elif (games_team1 >= 7 or games_team2 >= 7) and (games_diff >= 1):
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

    def _calc_won_games(self) -> tuple[int, int]:
        """Returns as a tuple of (nb_won_games_team1, nb_won_games_team2)"""
        nb_won_games_team1 = 0
        nb_won_games_team2 = 0
        # Team 1
        games_t1 = [self.games_set1_team1, self.games_set2_team1, self.games_set3_team1]
        for nb_games in games_t1:
            if nb_games is not None:
                nb_won_games_team1 += nb_games
        # Team 2
        games_t2 = [self.games_set1_team2, self.games_set2_team2, self.games_set3_team2]
        for nb_games in games_t2:
            if nb_games is not None:
                nb_won_games_team2 += nb_games
        self.nb_won_games_team1 = nb_won_games_team1
        self.nb_won_games_team2 = nb_won_games_team2
        self.nb_won_games_diff = abs(nb_won_games_team1 - nb_won_games_team2)
        self.won_games = (nb_won_games_team1, nb_won_games_team2)
        return self.won_games

    def calc_won_sets_and_games(self) -> tuple[int, int]:
        """Returns as a tuple of (nb_won_sets_team1, nb_won_sets_team2)"""
        self.check_final_validity()
        self._calc_won_games()
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
    def from_string(cls, score_string: str, is_finished: bool = True) -> Self:
        """Create a MatchScore object from string "comma-separated" formatted as i.e:
        "6-4, 3-6, 6-2"

        Examples
        --------
        >>> score = MatchScore.from_string("6-4, 3-6, 6-2")
        """
        list_sets = score_string.replace(" ", "")  # Remove spaces
        list_sets = list_sets.split(",")

        list_games = []
        while len(list_sets) > 0:
            current_set = list_sets.pop(0)
            games_team1 = current_set.split("-")[0]
            list_games.append(games_team1)
            games_team2 = current_set.split("-")[1]
            list_games.append(games_team2)

        while len(list_games) < 6:
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
        if is_finished:
            match_score.calc_won_sets_and_games()
        return match_score


class Match(ValidatedSQLModel, table=True):
    teams: list[Team] = Relationship(back_populates="matches", link_model=LinkTeamMatch)
    players: list[Player] = Relationship(
        back_populates="matches", link_model=LinkPlayerMatch
    )
    date: datetime = Field(
        default_factory=now,
        description="Match execution date",
        sa_column=Column(DateTime(timezone=True)),
    )
    score: str | None = Field(None, description="string formatted as '6-4, 7-5'")
    team1_won: bool | None = Field(
        None, description="True/False if team1_won. None for no winner"
    )
    nb_won_sets_diff: NonNegativeInt | None = Field(None, le=3)
    nb_won_games_diff: NonNegativeInt | None = Field(None, le=16)
    # Auto data creation
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str | None = Field(None, index=True, description="as 'p1/p2 vs p3/p4'")
    creation_date: datetime = Field(
        default_factory=now,
        description="Creation in db",
        sa_column=Column(DateTime(timezone=True)),
    )

    def _set_match_name(self) -> None:
        self.name = f"{str(self.teams[0])} vs {str(self.teams[1])}"

    def validate_players(self):
        nb_players = len(self.players)
        if nb_players != 4:
            raise ValueError(f"a match must have exactly 4 players. Got {nb_players=}")
        nb_teams = len(self.teams)
        if nb_teams != 2:
            raise ValueError(f"a match must have exactly 2 teams. Got {nb_teams=}")

    def post_init(self):
        """Validate players nb and set match name"""
        self.validate_players()
        self._set_match_name()

    def get_winners_losers(
        self,
    ) -> list[Team, Team]:  # tuple[list[Player], list[Player]]:
        """"""
        self.validate_players()
        match_score = MatchScore.from_string(self.score)
        match_score.calc_won_sets_and_games()
        self.nb_won_sets_diff = match_score.nb_won_sets_diff
        self.nb_won_games_diff = match_score.nb_won_games_diff
        if match_score.nb_won_sets_team1 > match_score.nb_won_sets_team2:
            winners = self.teams[0]
            losers = self.teams[1]
            self.team1_won = True
        elif match_score.nb_won_sets_team1 < match_score.nb_won_sets_team2:
            losers = self.teams[0]
            winners = self.teams[1]
            self.team1_won = False
        else:
            raise MatchNotFinishedError(f"no winner yet ({match_score = })")
        return winners, losers
