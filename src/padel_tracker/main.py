# Must keep this line below to init all SQLModel defined
from padel_tracker import models as models
from padel_tracker.utils.logs import init_loggings
from padel_tracker.database.db import create_db_and_tables

LOG_LEVEL = None  # "WARN"

def init_app()->None:
    init_loggings(log_level=LOG_LEVEL)
    create_db_and_tables()
