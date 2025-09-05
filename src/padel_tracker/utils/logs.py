import sys

from loguru import logger

from padel_tracker.utils.datetime_utils import now, DATETIME_TZ_FR
from padel_tracker.utils.conf import DICT_CONF
from padel_tracker.database.db import commit_to_db_no_session
from padel_tracker.models.base import Logs

# Define/get fixed params
MAIN_LOG_NAME = "PT"
LOG_FORMAT = "<green>{time:DD/MM/YYYY HH:mm:ssZZ}</green> - {extra[name]:<16} - <level>{level:<7}</level>  - {message}"
LOG_LEVEL_CONSOLE = DICT_CONF["general"]["log_level_console"]
LOG_LEVEL_DB = DICT_CONF["general"]["log_level_db"]


# Setup custom sinks for console + database
def _convert_to_timezone(record):
    record["time"] = record["time"].astimezone(DATETIME_TZ_FR)
    return record


logger.remove()
logger = logger.patch(_convert_to_timezone)
logger.add(sys.stderr, format=LOG_FORMAT, level=LOG_LEVEL_CONSOLE)


def _database_log_sink(loguru_message) -> None:
    """Create a custom SQLModel 'Logs' and commit it for recording a log in database"""
    try:
        record = loguru_message.record
        log_record = Logs(
            timestamp=now(),
            name=str(record["extra"]["name"]),
            level=str(record["level"].name),
            message=str(record["message"]),
        )
        commit_to_db_no_session(log_record)
    except Exception as exc:
        print(f"failed to log to database: {exc}")


logger.add(_database_log_sink, level=LOG_LEVEL_DB, filter="padel_tracker", enqueue=True)


# Define main "get_logger" function to be called from elsewhere
def get_logger(name: str = "", use_app_name: bool = True) -> type(logger):
    """
    Returns dedicated Loguru logger object with custom 'MAIN_LOG_NAME.name' in the 'extra',
    allowing to display a custom name of location in the log messages (to mimic std logging behaviour).
    If no 'name', will return logger with 'MAIN_LOG_NAME' as name only

    Examples
    --------
    >>> logger = get_logger('my_function')
    >>> logger.warning('This is a local warning from blabla')
    ## Will output to MAIN_LOG_NAME.my_function logger
    """
    logger_name = ""
    if use_app_name:
        logger_name = f"{MAIN_LOG_NAME}."
    if name:
        logger_name += f"{name}"
    return logger.bind(name=logger_name)
