from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Self

# TODO : from sqlmodel import SQLModel, Field
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat, NonNegativeInt

from padel_tracker.utils.datetime_utils import now
from padel_tracker.utils.validation import ensure_frozen_field
from padel_tracker.models.ranking import (
    ELO_BASE_RATING,
    ELO_BASE_K,
    calc_team_expected_elo_score,
    calc_team_elo_rating,
)


class Player(BaseModel, validate_assignment=True):  # table=True,
    name: str
    nickname: Optional[str] = Field(None, description="Player nickname, a la espanola")
    id: UUID = Field(default_factory=uuid4, primary_key=True, repr=False)
    nb_matches: NonNegativeInt = Field(0, description="Total number of played matches")
    nb_victories: NonNegativeInt = Field(0, description="Total number of victories")
    nb_defeats: NonNegativeInt = Field(0, description="Total number of defeats")
    elo_rating: PositiveInt = Field(ELO_BASE_RATING, description="Current Elo rating")
    elo_k: PositiveFloat = Field(ELO_BASE_K, description="K value for Elo calc")
    rank: Optional[PositiveInt] = Field(None, description="Current rank in the league")
    best_rank: Optional[PositiveInt] = Field(
        None, description="Best achieved rank ever"
    )
    best_elo_rating: Optional[PositiveInt] = Field(
        ELO_BASE_RATING, description="Best achieved Elo rating"
    )
    creation_date: datetime = Field(
        default_factory=now,
        description="Date of creation of player in database",
        repr=False,
    )
    updated_date: datetime = Field(
        default_factory=now,
        description="Latest update date of Elo score",
        repr=False,
    )

    # TODO (prio 3)
    # best_teammate : Player

    def __setattr__(self, key, value):
        # Ensure field is not "read-only"
        frozen_fields = {"id", "creation_date"}
        ensure_frozen_field(self, key, frozen_fields)
        # Write assignment
        super().__setattr__(key, value)
        # Update "updated_date" if applicable
        triggers_timestamp_update = {"nb_matches", "elo_rating", "rank"}
        if key in triggers_timestamp_update:
            super().__setattr__("updated_date", now())


class Team(BaseModel):
    player1: Player
    player2: Player
    # id: UUID = Field(default_factory=uuid4, repr=False)
    elo_rating: PositiveInt = Field(None, description="Avg of both players")

    def calc_team_elo_rating(self) -> int:
        self.elo_rating = calc_team_elo_rating(
            self.player1.elo_rating,
            self.player2.elo_rating,
        )
        return self.elo_rating

    def calc_team_expected_elo_score(self, opponent_team: Self) -> float:
        return calc_team_expected_elo_score(
            self.calc_team_elo_rating(), opponent_team.calc_team_elo_rating()
        )

    def __repr__(self):
        p1_str = self.player1.nickname if self.player1.nickname else self.player1.name
        p2_str = self.player2.nickname if self.player2.nickname else self.player2.name
        return f"{p1_str}-{p2_str}"


if __name__ == "__main__":
    p1 = Player(name="Coucou")
    p2 = Player(name="mabite")
    print(p1)
    p1.elo_rating = 122
    print(p1)
    t1 = Team(player1=p1, player2=p2)
    print(t1.calc_team_elo_rating())
    print("bye")
