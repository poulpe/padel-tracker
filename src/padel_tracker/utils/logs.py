import logging
from concurrent.futures.thread import ThreadPoolExecutor

from padel_tracker.utils.datetime_utils import now
from padel_tracker.utils.conf import DICT_CONF, DBMode, RunMode
from padel_tracker.database.db import Database, DB, commit_to_db_no_session
from padel_tracker.models.base import Logs

# Define custom log level for notif from main (between INFO and WARNING)
LOG_LEVEL_NOTIF = 25
logging.addLevelName(LOG_LEVEL_NOTIF, "NOTIF")

# Define parameters
MAIN_LOG_NAME = "PT"
DEFAULT_LOG_LEVEL_CONSOLE = logging.INFO
DEFAULT_LOG_LEVEL_DB = LOG_LEVEL_NOTIF
DEFAULT_LOG_FORMATTER = logging.Formatter(
    fmt="%(asctime)s - %(name)-16s - %(levelname)-6s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)
logging.Formatter.converter = lambda *args: now().timetuple()


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


class DatabaseLogHandler(logging.Handler):
    """Use of custom SQLModel 'Logs' for recording a log in local database"""

    def __init__(
        self,
        db: Database = DB,
        is_threaded: bool = False,
        thread_pool: ThreadPoolExecutor = None,
        thread_workers: int = 4,
    ):
        super().__init__()
        self.db = db
        self.is_threaded = is_threaded
        if is_threaded:
            if thread_pool:
                self.thread_pool = thread_pool
            else:
                self.thread_pool = ThreadPoolExecutor(max_workers=thread_workers)

    def emit(self, record):
        try:
            log_record = Logs(
                timestamp=now(),
                name=record.name,
                level=record.levelname,
                message=record.getMessage(),
            )
            if self.is_threaded:
                self.thread_pool.submit(commit_to_db_no_session, log_record, db=self.db)
            else:
                commit_to_db_no_session(log_record, db=self.db)
        except Exception as e:
            print(f"Failed to log to database: {e}")

    def close(self):
        """Close properly the ThreadPoolExecutor"""
        if self.is_threaded:
            self.thread_pool.shutdown(wait=True)
        super().close()


class LoggerWithNotif(logging.Logger):
    """Standard logger but allowing logging "notif" with the custom LOG_NOTIF_LEVEL"""

    def __init__(self, name: str, level: int | str = 0):
        super().__init__(name=name, level=level)

    def notif(
        self,
        msg: object,
        *args: object,
        exc_info=None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra=None,
    ) -> None:
        self.log(
            LOG_LEVEL_NOTIF,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )


logging.setLoggerClass(LoggerWithNotif)  # Important to register as default, must keep


def init_loggings(
    log_level_console: str | int = None,
    log_level_db: str | int = DEFAULT_LOG_LEVEL_DB,
    db_mode: DBMode = None,
    run_mode: RunMode = None,
    db: Database = DB,
    is_threaded: bool = True,
    thread_pool: ThreadPoolExecutor = None,
    silent: bool = False,
) -> LoggerWithNotif:

    main_logger = logging.getLogger(MAIN_LOG_NAME)
    main_logger.setLevel("DEBUG")

    # Get default parameters if None
    if log_level_console is None:
        try:
            log_level_console = DICT_CONF["general"]["log_level_console"]
        except KeyError:
            log_level_console = DEFAULT_LOG_LEVEL_CONSOLE
    if db_mode is None:
        try:
            db_mode = DBMode(DICT_CONF["general"]["db_mode"].lower())
        except (KeyError, ValueError):
            db_mode = DBMode.LOCAL
    if run_mode is None:
        try:
            run_mode = RunMode(DICT_CONF["general"]["run_mode"].lower())
        except (KeyError, ValueError):
            run_mode = RunMode.DEBUG

    # Check if loggings have already been init (to return fast if not needed)
    init_msg = f"init with conf: db_mode={str(db_mode)}, run_mode={str(run_mode)}, {log_level_console=}, {log_level_db=}"
    if main_logger.hasHandlers():
        # Log starting message logging
        if not silent:
            main_logger.getChild("init_logs").info(init_msg)
        return

    # Add console handler
    log_handler_console = NoTracebackStreamHandler()
    log_handler_console.setFormatter(DEFAULT_LOG_FORMATTER)
    log_handler_console.setLevel(log_level_console)
    main_logger.addHandler(log_handler_console)

    # Add database handler
    log_handler_database = DatabaseLogHandler(
        db=db, is_threaded=is_threaded, thread_pool=thread_pool
    )
    log_handler_database.setLevel(log_level_db)
    main_logger.addHandler(log_handler_database)

    # Log starting message logging
    if not silent:
        main_logger.getChild("init_logs").info(init_msg)

    return main_logger


def get_logger(
    log_name: str = "",
    log_level: str | int = None,
) -> LoggerWithNotif:
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
        init_loggings(silent=True)
    # Create logger
    if log_name:
        logger_name = f"{MAIN_LOG_NAME}.{log_name}"
    else:
        logger_name = MAIN_LOG_NAME
    logger = logging.getLogger(logger_name)
    if log_level is not None and log_name:
        logger.setLevel(log_level)
    return logger
