from datetime import datetime
from uuid import UUID, uuid4

from pydantic import NonNegativeInt
from sqlmodel import Field, Relationship, Column, DateTime

from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.base import ValidatedSQLModel
from padel_tracker.models.links import (
    LinkPlayerLeague,
    LinkLeagueMatch,
    LinkTeamLeague,
    LinkLeagueadminUser,
    LinkEventLeague,
)
from padel_tracker.models.players import RankHistory


class League(ValidatedSQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(
        index=True,
        min_length=2,
        max_length=64,
        schema_extra={"pattern": r"^[\p{L}' -]*[\p{L}][\p{L}][\p{L}' -]*$"},
    )
    is_private: bool | None = Field(False)
    description: str | None = Field(
        None, description="Friendly text for users", max_length=256
    )
    creation_date: datetime = Field(
        default_factory=now,
        description="Date of creation in database",
        repr=False,
        sa_column=Column(DateTime(timezone=True)),
    )
    # History data
    nb_matches: NonNegativeInt = Field(0)
    nb_players: NonNegativeInt = Field(0)
    last_match_date: datetime | None = Field(
        None,
        sa_column=Column(DateTime(timezone=True)),
    )
    # Links with other tables
    player_links: list[LinkPlayerLeague] = Relationship(back_populates="league")
    matches: list["Match"] = Relationship(
        back_populates="league", link_model=LinkLeagueMatch
    )
    rank_history: list["RankHistory"] = Relationship(back_populates="league")
    teams: list["Team"] = Relationship(
        back_populates="leagues", link_model=LinkTeamLeague
    )
    admin_users: list["User"] = Relationship(
        back_populates="admin_leagues", link_model=LinkLeagueadminUser
    )
    events: list["Event"] = Relationship(
        back_populates="leagues",
        link_model=LinkEventLeague,
    )
