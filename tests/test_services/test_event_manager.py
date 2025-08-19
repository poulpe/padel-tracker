import pytest

from padel_tracker.utils.datetime_utils import make_datetime


def test_make_dummy_event(make_dummy_event):
    event = make_dummy_event(
        name="Big event",
        date=make_datetime(day=12, month=12, year=2025, hour=19, minute=30),
        category="season_reset",
        description="Si, mucho reset",
    )
    assert event.name == "Big event"

    with pytest.raises(ValueError):
        make_dummy_event(
            name="NOK event",
            date=make_datetime(day=12, month=12, year=2025, hour=19, minute=30),
            category="This is not a correct category !!",
        )
