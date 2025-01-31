import logging
from pathlib import Path

import supabase  # Cloud loggings

from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.utils.datetime_utils import now
from padel_tracker.utils.conf import DICT_CONF, DB_MODE_TYPE, RUN_MODE_TYPE
from padel_tracker.database.db import commit_to_db_no_session
from padel_tracker.models.base import Logs

# Define custom log level for notif from main (between INFO and WARNING)
LOG_LEVEL_NOTIF = 25
logging.addLevelName("NOTIF", LOG_LEVEL_NOTIF)

# Define parameters
MAIN_LOG_NAME = "PadelTracker"
DEFAULT_LOG_LEVEL_CONSOLE = logging.INFO
DEFAULT_LOG_LEVEL_FILE = LOG_LEVEL_NOTIF
DEFAULT_LOG_FOLDER = get_absolute_path(__file__, "../../../data/logs/")
DEFAULT_LOG_FORMATTER = logging.Formatter(
    fmt="%(asctime)s - %(name)-41s - %(levelname)-6s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)
logging.Formatter.converter = lambda *args: now().timetuple()

DEFAULT_LOG_PARAMETERS = {
    "log_level": DEFAULT_LOG_LEVEL_CONSOLE,
    "log_level_file": DEFAULT_LOG_LEVEL_FILE,
    "log_file_folder": DEFAULT_LOG_FOLDER,
}


class NoTracebackStreamHandler(logging.StreamHandler):
    """Logging Streamhandler but without logging traceback when logger.exception()"""

    def handle(self, record):
        info, cache = record.exc_info, record.exc_text
        record.exc_info, record.exc_text = None, None
        try:
            super().handle(record)
        finally:
            record.exc_info = info
            record.exc_text = cache


class LocalDatabaseLogHandler(logging.Handler):
    """Use of custom SQLModel 'Logs' for recording a log in local database"""

    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            log_record = Logs(
                timestamp=now(),
                name=record.name,
                level=record.levelname,
                message=record.getMessage(),
            )
            commit_to_db_no_session(log_record)
        except Exception as e:
            print(f"Failed to log to local database: {e}")


def create_supabase_client():
    return supabase.create_client(
        supabase_url=DICT_CONF["db_credentials"]["supabase_api_url"],
        supabase_key=DICT_CONF["db_credentials"]["supabase_api_key"],
    )


class SupabaseLogHandler(logging.Handler):
    def __init__(self, supabase_client: supabase.Client):
        super().__init__()
        self.supabase_client = supabase_client

    def emit(self, record):
        try:
            # Make log record
            log_entry = {
                "timestamp": str(now()),
                "name": record.name,
                "level": record.levelname,
                "message": record.getMessage(),
            }
            # Insert in Supabase logs table
            self.supabase_client.table("logs").insert(log_entry).execute()
        except Exception as e:
            print(f"Failed to log to Supabase: {e}")


def get_logger(
    log_name: str = "",
    log_level: str | int = None,
) -> logging.Logger:
    """
    Returns a dedicated logger, allowing to display a custom name of location in the log messages
    If log_level is given, the returned logger will be set to the requested level.
    Else it will use current log level of root logger.

    Parameters
    ----------
    log_name:str, optional
        Logger name
    log_level:str, optional
        Logger level

    Examples
    --------
    >>> logger = get_logger('my_function')
    >>> logger.warning('This is a local warning from blabla')
    ## Will output to MAIN_LOG_NAME.my_function logger

    >>> logger = get_logger('my_object_to_debug', log_level='DEBUG')
    """
    # If loggings have not been init, init them
    if not logging.getLogger(MAIN_LOG_NAME).hasHandlers():
        init_loggings()
    # Create logger
    if log_name:
        logger_name = f"{MAIN_LOG_NAME}.{log_name}"
    else:
        logger_name = MAIN_LOG_NAME
    logger = logging.getLogger(logger_name)
    if log_level is not None and log_name:
        logger.setLevel(log_level)
    return logger


def init_loggings(
    log_level_console: str | int = None,
    log_file_folder: str | Path = None,
    log_level_file: str | int = None,
    db_mode: DB_MODE_TYPE = None,
    run_mode: RUN_MODE_TYPE = None,
) -> logging.Logger:
    # Check if loggings have already been init (to return fast if not needed)
    main_logger = logging.getLogger(MAIN_LOG_NAME)
    if main_logger.hasHandlers():
        return
    main_logger.setLevel("DEBUG")

    # Get default parameters if None
    if log_level_console is None:
        try:
            log_level_console = DICT_CONF["general"]["log_level_console"]
        except KeyError:
            log_level_console = DEFAULT_LOG_PARAMETERS["log_level"]
    if log_file_folder is None:
        log_file_folder = DEFAULT_LOG_PARAMETERS["log_file_folder"]
    if log_level_file is None:
        log_level_file = DEFAULT_LOG_PARAMETERS["log_level_file"]
    if db_mode is None:
        try:
            db_mode = DICT_CONF["general"]["db_mode"]
        except KeyError:
            db_mode = "local"
    if run_mode is None:
        try:
            run_mode = DICT_CONF["general"]["run_mode"]
        except KeyError:
            run_mode = "test"

    # Convert log levels to take into account custom NOTIF level
    # log_level = logging.getLevelName(log_level)
    # log_level_file = logging.getLevelName(log_level_file)

    # Add console handler
    log_handler_console = NoTracebackStreamHandler()  # logging.StreamHandler()
    log_handler_console.setFormatter(DEFAULT_LOG_FORMATTER)
    log_handler_console.setLevel(log_level_console)
    main_logger.addHandler(log_handler_console)

    # Add localdatabase handler for local mode
    if db_mode.lower() == "local":
        log_handler_local_database = LocalDatabaseLogHandler()
        log_handler_local_database.setFormatter(DEFAULT_LOG_FORMATTER)
        log_handler_local_database.setLevel(log_level_file)
        main_logger.addHandler(log_handler_local_database)

    # Add Cloud Supabase handler for "cloud" mode
    if db_mode.lower() == "cloud":
        supabase_client = create_supabase_client()
        log_handler_supabase = SupabaseLogHandler(supabase_client=supabase_client)
        log_handler_supabase.setFormatter(DEFAULT_LOG_FORMATTER)
        log_handler_supabase.setLevel(log_level_file)
        main_logger.addHandler(log_handler_supabase)

    # Log starting message logging
    msg = f"initialized logs with conf: {db_mode=}, {run_mode=}, {log_level_console=}, {log_level_file=}"
    main_logger.getChild("init_loggings").log(LOG_LEVEL_NOTIF, msg)

    return main_logger


def set_logging_level(log_level: str | int) -> None:
    logging.getLogger(MAIN_LOG_NAME).setLevel(log_level)


def disable_loggings() -> None:
    logging.getLogger(MAIN_LOG_NAME).setLevel(logging.CRITICAL)
