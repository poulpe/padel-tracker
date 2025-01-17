from datetime import datetime
from zoneinfo import ZoneInfo

TZ_FR = ZoneInfo("Europe/Paris")


def now() -> datetime:
    return datetime.now(TZ_FR)


def make_datetime(day, month, year) -> datetime:
    return datetime(day=day, month=month, year=year, tzinfo=TZ_FR)
