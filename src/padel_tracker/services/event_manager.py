"""
CRUD on Events
"""

from uuid import UUID
from datetime import datetime

import pandas as pd

from padel_tracker.utils.logs import get_logger
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.models.events import Event, EventCategory
from padel_tracker.models.leagues import League
from padel_tracker.models.links import LinkEventLeague
from padel_tracker.services import league_manager

LOGGER_NAME = "events"
LOGGER = get_logger(LOGGER_NAME)


def create_event(
    session: Session,
    name: str,
    date: datetime,
    category: EventCategory | str = None,
    description: str = "",
    end_date: datetime = None,
    league_name: str = "",
) -> Event:
    """Create an event
    If no `league_name` is specified, it will declare this event for all existing leagues
    """
    logger = get_logger(f"{LOGGER_NAME}.create")

    # Create and commit it to get ID
    if category and not isinstance(category, EventCategory):
        category = EventCategory(category)
    event = Event(
        name=name,
        date=date,
        category=category,
        description=description,
        end_date=end_date,
    )
    commit_to_db(event, session=session)
    logger.info("valid event creation, now busy assigning to relevant league(s)")

    # Assign to leagues
    if league_name:
        league = league_manager.get_league_from_name(session=session, name=league_name)
        list_leagues = [league]
    else:
        list_leagues = league_manager.get_all_leagues(session=session, as_df=False)
    list_objects_to_commit = []
    for league in list_leagues:
        event.leagues.append(league)
        league.events.append(event)
        list_objects_to_commit.append(league)
    commit_to_db(event, *list_objects_to_commit, session=session)

    logger.success(f"created {event = }")
    return event


def get_all_events_from_league(
    session: Session,
    league_name: str,
    as_df: bool = False,
    order_by=None,
    order_descending: bool = False,
) -> list[Event] | pd.DataFrame:
    # Fecth league
    league_id = read_from_db(
        League.id, where=League.name == league_name, unique=True, session=session
    )
    # Fetch list of event ids from the league
    event_ids = read_from_db(
        LinkEventLeague.event_id,
        where=LinkEventLeague.league_id == league_id,
        session=session,
    )
    return read_from_db(
        Event,
        where=Event.id.in_(event_ids),
        session=session,
        as_df=as_df,
        order_by=order_by,
        order_descending=order_descending,
    )


def get_last_season_reset_event(session: Session) -> Event:
    event = read_from_db(
        Event,
        where=Event.category == EventCategory.SEASON_RESET,
        order_by=Event.date,
        order_descending=True,
        limit_first=1,
        unique=True,
        session=session,
    )
    # TODO (prio2) : sanity check on event (exists, ...)
    return event


def delete_event(session: Session, event_id: UUID | str) -> None:
    logger = get_logger(f"{LOGGER_NAME}.delete")

    if isinstance(event_id, str):
        event_id = UUID(event_id)

    # Fetch event
    try:
        event = read_from_db(
            Event, where=Event.id == event_id, unique=True, session=session
        )
    except Exception as exc:
        logger.exception(exc)
        raise (exc)
    event_name = event.name
    event_date = event.date

    delete_from_db(event, session=session)
    logger.success(f"deleted Event({event_name=}, {event_id=}, {event_date=})")
