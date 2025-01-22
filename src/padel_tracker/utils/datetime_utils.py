import datetime
from zoneinfo import ZoneInfo

TZ_FR = ZoneInfo("Europe/Paris")


def now() -> datetime.datetime:
    """Returns datetime.datetime.now() with Timezone Europe/Paris"""
    return datetime.datetime.now(TZ_FR)


def make_datetime(day, month, year, hour=18, minute=30) -> datetime.datetime:
    """Returns datetime.datetime object with Timezone Europe/Paris"""
    return datetime.datetime(
        day=day, month=month, year=year, hour=hour, minute=minute, tzinfo=TZ_FR
    )


def make_datetime_from_combi(
    date: datetime.date, time: datetime.time
) -> datetime.datetime:
    """Returns datetime.datetime object with Timezone Europe/Paris"""
    return datetime.datetime.combine(date, time, tzinfo=TZ_FR)
