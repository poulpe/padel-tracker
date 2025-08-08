from datetime import datetime
from uuid import UUID, uuid4
from enum import StrEnum, auto
from typing import Optional

from pydantic import NonNegativeInt
from sqlmodel import Field, Relationship, Column, DateTime

from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.base import ValidatedSQLModel
from padel_tracker.models.links import LinkLeagueadminUser


class UserRole(StrEnum):
    GUEST = auto()
    PLAYER = auto()
    TRUSTEDPLAYER = auto()
    ADMIN = auto()


class User(ValidatedSQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    auth_user_id: str = Field(
        unique=True,
        index=True,
        description="'sub' key in st.user",
        repr=False,
    )
    player_id: UUID | None = Field(default=None, foreign_key="player.id")
    player: Optional["Player"] = Relationship(back_populates="user")
    creation_date: datetime = Field(
        default_factory=now,
        description="Date of creation of user in database",
        repr=False,
        sa_column=Column(DateTime(timezone=True)),
    )
    last_visit_date: datetime | None = Field(
        default=None,
        description="Last date user logged in the web application",
        sa_column=Column(DateTime(timezone=True)),
    )
    nb_visits: NonNegativeInt = Field(0, description="Total visits on the web app")
    # Personalization
    email: str | None = Field(default=None)
    email_verified: bool = Field(default=False, repr=False)
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=32,
        schema_extra={"pattern": r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ '’.-]{1,}$"},
    )
    role: str = Field(default=UserRole.PLAYER)
    picture_url: str | None = Field(default=None, repr=False)
    # App settings
    default_language: str | None = Field(None)
    # Leagues
    default_league_name: str | None = Field(None)
    admin_leagues: list["League"] = Relationship(
        back_populates="admin_users",
        link_model=LinkLeagueadminUser,
    )
