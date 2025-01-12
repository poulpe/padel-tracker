from datetime import datetime
from zoneinfo import ZoneInfo

TZ_FR = ZoneInfo("Europe/Paris")


def now() -> datetime:
    return datetime.now(TZ_FR)
