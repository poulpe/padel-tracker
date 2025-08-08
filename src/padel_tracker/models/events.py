from uuid import UUID, uuid4
from datetime import datetime
from enum import StrEnum, auto

from sqlmodel import Field, Column, DateTime, Relationship

from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.base import ValidatedSQLModel
from padel_tracker.models.links import LinkEventLeague


class EventCategory(StrEnum):
    SEASON_RESET = auto()
    TOURNAMENT = auto()
    MISC = auto()


class Event(ValidatedSQLModel, table=True):
    """To declare events like season resets, tournaments..."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=64)
    date: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), index=True)
    )
    # Optional
    category: str | None = Field(None)
    description: str | None = Field(None, max_length=256, repr=False)
    end_date: datetime | None = Field(
        None, sa_column=Column(DateTime(timezone=True), index=True)
    )
    # Link with league
    leagues: list["League"] = Relationship(
        back_populates="events",
        link_model=LinkEventLeague,
    )
