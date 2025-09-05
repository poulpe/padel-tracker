# Must keep this line below to init all SQLModel defined
from padel_tracker import models as models
from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.conf import get_conf_message
from padel_tracker.database.db import init_db_and_tables


def init_app() -> None:
    """Create database tables if they don't exist"""
    init_db_and_tables()
    get_logger("init").info(f"init with conf: {get_conf_message()}")
