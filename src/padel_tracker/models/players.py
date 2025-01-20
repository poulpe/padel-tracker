from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from pydantic import PositiveInt, PositiveFloat, NonNegativeInt

from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.links import PlayerMatchLink, PlayerTeamLink, TeamMatchLink
from padel_tracker.models.ranking import (
    ELO_BASE_RATING,
    ELO_BASE_K,
    calc_team_elo_rating,
)

##### Player #####


class PlayerBase(SQLModel, validate_assignment=True):
    """Logic without links to Matches and history"""

    name: str = Field(index=True, min_length=2, max_length=32)
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    elo_rating: PositiveInt = Field(ELO_BASE_RATING, index=True)
    elo_k: PositiveFloat = Field(ELO_BASE_K, repr=False)
    rank: PositiveInt | None = Field(None, index=True, description="Rank in the league")
    creation_date: datetime = Field(
        default_factory=now,
        description="Date of creation of player in database",
        repr=False,
    )
    last_match_date: datetime | None = Field(
        default=None,
        description="Latest update date of Elo score",
        repr=False,
    )
    # History related
    nb_matches: NonNegativeInt = Field(0, description="Total number of played matches")
    nb_victories: NonNegativeInt = Field(0, description="Total number of victories")
    nb_defeats: NonNegativeInt = Field(0, description="Total number of defeats")
    best_elo_rating: PositiveInt = Field(
        ELO_BASE_RATING, description="Best achieved Elo rating ever", repr=False
    )
    best_rank: PositiveInt | None = Field(
        None, description="Best achieved rank ever", repr=False
    )


class EloRatingHistory(SQLModel, table=True, validate_assignment=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    player_id: UUID | None = Field(default=None, foreign_key="player.id")
    player_name: str = Field(description="For convenience")
    player: "Player" = Relationship(back_populates="elo_rating_history")
    # Actual data
    date: datetime = Field(default_factory=now, index=True)
    elo_rating: NonNegativeInt = Field()
    elo_rating_gain: int = Field()


class RankHistory(SQLModel, table=True, validate_assignment=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    player_id: UUID | None = Field(default=None, foreign_key="player.id")
    player_name: str = Field(description="For convenience")
    player: "Player" = Relationship(back_populates="rank_history")
    # Actual data
    date: datetime = Field(default_factory=now, index=True)
    rank: PositiveInt = Field()


class Player(PlayerBase, table=True):
    matches: list["Match"] = Relationship(
        back_populates="players", link_model=PlayerMatchLink
    )
    teams: list["Team"] = Relationship(
        back_populates="players", link_model=PlayerTeamLink
    )
    elo_rating_history: list[EloRatingHistory] = Relationship(back_populates="player")
    rank_history: list[RankHistory] = Relationship(back_populates="player")


##### Team #####


class TeamEloRatingHistory(SQLModel, table=True, validate_assignment=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    team_id: UUID | None = Field(default=None, foreign_key="team.id")
    team_name: str = Field(description="For convenience")
    team: "Team" = Relationship(back_populates="elo_rating_history")
    # Actual data
    date: datetime = Field(default_factory=now, index=True)
    elo_rating: NonNegativeInt = Field()
    elo_rating_gain: int = Field()


class Team(SQLModel, table=True):
    players: list[Player] = Relationship(
        back_populates="teams", link_model=PlayerTeamLink
    )
    matches: list["Match"] = Relationship(
        back_populates="teams", link_model=TeamMatchLink
    )
    id: UUID = Field(default_factory=uuid4, primary_key=True, repr=False)
    elo_rating: PositiveInt | None = Field(None, description="Avg of both players")
    name: str | None = Field(None, index=True, description="'p1-p2' alphabetical order")
    # History related
    last_match_date: datetime = Field(
        default_factory=now,
        description="Latest update date of Elo score",
        repr=False,
    )
    nb_matches: NonNegativeInt = Field(0, description="Total number of played matches")
    nb_victories: NonNegativeInt = Field(0, description="Total number of victories")
    nb_defeats: NonNegativeInt = Field(0, description="Total number of defeats")
    best_elo_rating: PositiveInt = Field(
        ELO_BASE_RATING, description="Best achieved Elo rating ever"
    )
    elo_rating_history: list[TeamEloRatingHistory] = Relationship(back_populates="team")

    def validate_players(self):
        nb_players = len(self.players)
        if nb_players != 2:
            raise ValueError(f"a team must have exactly 2 players. Got {nb_players=}")

    def calc_team_elo_rating(self) -> int:
        self.validate_players()
        self.elo_rating = calc_team_elo_rating(
            self.players[0].elo_rating,
            self.players[1].elo_rating,
        )
        return self.elo_rating

    def _set_team_name(self) -> None:
        self.validate_players()
        sorted_names = sorted([self.players[0].name, self.players[1].name])
        self.name = f"{sorted_names[0]}/{sorted_names[1]}"

    def __str__(self):
        if not self.name:
            self._set_team_name()
        return self.name

    @classmethod
    def get_name_from_players_name(cls, player1_name: str, player2_name: str):
        sorted_names = sorted([player1_name, player2_name])
        return f"{sorted_names[0]}/{sorted_names[1]}"

    def post_init(self):
        """Define name and elo_rating"""
        self.calc_team_elo_rating()
        self._set_team_name()
