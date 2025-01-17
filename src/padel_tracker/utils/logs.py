import logging
from pathlib import Path

from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.utils.datetime_utils import now

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
    if log_name:
        logger_name = f"{MAIN_LOG_NAME}.{log_name}"
    else:
        logger_name = MAIN_LOG_NAME
    logger = logging.getLogger(logger_name)
    if log_level is not None and log_name:
        logger.setLevel(log_level)
    return logger


def init_loggings(
    log_level: str | int = None,
    log_file_folder: str | Path = None,
    log_level_file: str | int = None,
) -> logging.Logger:
    # Get default parameters if None
    if log_level is None:
        log_level = DEFAULT_LOG_PARAMETERS["log_level"]
    if log_file_folder is None:
        log_file_folder = DEFAULT_LOG_PARAMETERS["log_file_folder"]
    if log_level_file is None:
        log_level_file = DEFAULT_LOG_PARAMETERS["log_level_file"]

    logger = logging.getLogger(MAIN_LOG_NAME)
    logger.setLevel("DEBUG")

    # Convert log levels to take into account custom NOTIF level
    # log_level = logging.getLevelName(log_level)
    # log_level_file = logging.getLevelName(log_level_file)

    # Remove all handlers (allows refreshing if called several times)
    if logger.hasHandlers():
        logger.handlers = []

    # Add console handler
    log_handler_console = NoTracebackStreamHandler()  # logging.StreamHandler()
    log_handler_console.setFormatter(DEFAULT_LOG_FORMATTER)
    log_handler_console.setLevel(log_level)
    logger.addHandler(log_handler_console)

    # Add file handler
    if log_file_folder:
        # Ensure log folder exists
        if not log_file_folder.exists():
            log_file_folder.mkdir(parents=True)
        # Add standard log file
        std_log_file = log_file_folder / "padeltracker.log"
        log_handler_file = logging.FileHandler(std_log_file)
        log_handler_file.setFormatter(DEFAULT_LOG_FORMATTER)
        log_handler_file.setLevel(log_level_file)
        logger.addHandler(log_handler_file)
        # Add log file for ERRORS and above only
        err_log_file = log_file_folder / "errors.log"
        log_handler_file = logging.FileHandler(err_log_file)
        log_handler_file.setFormatter(DEFAULT_LOG_FORMATTER)
        log_handler_file.setLevel("ERROR")
        logger.addHandler(log_handler_file)

    return logger


# Init loggings according to config / paths defaults
# try:
#     CONFIG_LOG_LEVEL_CONSOLE = DICT_CONFIG["logs"]["log_level_console"]
# except KeyError:
#     CONFIG_LOG_LEVEL_CONSOLE = DEFAULT_LOG_LEVEL_CONSOLE
#
# try:
#     CONFIG_LOG_LEVEL_FILE = DICT_CONFIG["logs"]["log_level_file"]
# except KeyError:
#     CONFIG_LOG_LEVEL_FILE = DEFAULT_LOG_LEVEL_FILE

# def init_loggings() -> None:
#
#     _init_loggings_with_parameters(
#         log_level=DEFAULT_LOG_LEVEL_CONSOLE,
#         log_file_folder=DEFAULT_LOG_FOLDER,
#         log_level_file=DEFAULT_LOG_LEVEL_FILE,
#     )
