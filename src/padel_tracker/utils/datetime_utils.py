from datetime import datetime
from zoneinfo import ZoneInfo

TZ_FR = ZoneInfo("Europe/Paris")


def now() -> datetime:
    return datetime.now(TZ_FR)


def make_datetime(day, month, year, hour=18, minute=30) -> datetime:
    return datetime(day=day, month=month, year=year, hour=hour, minute=minute, tzinfo=TZ_FR)
