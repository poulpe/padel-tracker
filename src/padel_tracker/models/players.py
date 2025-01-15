from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from pydantic import PositiveInt, PositiveFloat, NonNegativeInt

from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.links import PlayerMatchLink
from padel_tracker.models.ranking import (
    ELO_BASE_RATING,
    ELO_BASE_K,
)

class PlayerBase(SQLModel, validate_assignment=True):
    """Logic without links to Matches and history"""
    name: str = Field(index=True, description="Player nickname, a la espanola")
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    elo_rating: PositiveInt = Field(ELO_BASE_RATING, index=True, description="Current Elo rating")
    elo_k: PositiveFloat = Field(ELO_BASE_K, description="K value for Elo calc")
    rank: Optional[PositiveInt] = Field(None, index=True, description="Current rank in the league")
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
    # History related
    nb_matches: NonNegativeInt = Field(0, description="Total number of played matches")
    nb_victories: NonNegativeInt = Field(0, description="Total number of victories")
    nb_defeats: NonNegativeInt = Field(0, description="Total number of defeats")
    best_elo_rating: PositiveInt = Field(
        ELO_BASE_RATING, description="Best achieved Elo rating ever"
    )
    best_rank: Optional[PositiveInt] = Field(
        None, description="Best achieved rank ever"
    )

class Player(PlayerBase, table=True):
    matches:list["Match"] = Relationship(back_populates="players", link_model=PlayerMatchLink)
    #teams:list["Team"] = Relationship(back_populates="players", link_model=PlayerTeamLink)
    #TODO : elo_rating_history:dict[datetime, PositiveInt] = Field(None, repr=False)

    # def init_elo_rating_history(self) -> None:
    #     if self.elo_rating_history is None:
    #         self.elo_rating_history = {self.creation_date:self.elo_rating}
    #     else:
    #         raise AttributeError("tried to re-init existing history")

# TOCHECK (prio3) : use Teams ?

# class Team(SQLModel, table=True):
#     players:list[Player] = Relationship(back_populates="teams", link_model=PlayerTeamLink)
#     matches:list["Match"] = Relationship(back_populates="teams", link_model=TeamMatchLink)
#     id: UUID = Field(default_factory=uuid4, primary_key=True, repr=False)
#     elo_rating: PositiveInt | None = Field(None, description="Avg of both players")
#     name:str|None = Field(None, description="Team name as 'player1-player2', in alphabetical order")
#     # History related
#     nb_matches: NonNegativeInt = Field(0, description="Total number of played matches")
#     nb_victories: NonNegativeInt = Field(0, description="Total number of victories")
#     nb_defeats: NonNegativeInt = Field(0, description="Total number of defeats")
#     best_elo_rating: PositiveInt = Field(
#         ELO_BASE_RATING, description="Best achieved Elo rating ever"
#     )
#
#     def ensure_two_players(self):
#         nb_players = len(self.players)
#         if nb_players != 2:
#             raise ValueError(f"a team must be composed of exactly 2 players. Got {nb_players=}")
#
#     def calc_team_elo_rating(self) -> int:
#         self.ensure_two_players()
#         self.elo_rating = calc_team_elo_rating(
#             self.players[0].elo_rating,
#             self.players[1].elo_rating,
#         )
#         return self.elo_rating
#
#     def _set_team_name(self) -> None:
#         self.ensure_two_players()
#         sorted_names = sorted([self.players[0].name, self.players[1].name])
#         self.name =  f"{sorted_names[0]}/{sorted_names[1]}"
#
#     def post_init(self):
#         """Define name and elo_rating"""
#         self.calc_team_elo_rating()
#         self._set_team_name()

if __name__ == "__main__":
    p1 = PlayerBase(name="Coucou")
    p2 = PlayerBase(name="mabite")
    print(p1)
    p1.elo_rating = 122
    print(p1)
    print("bye")