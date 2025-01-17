"""
PadelPunto ?
"""

__version__ = "0.0.1"

from padel_tracker.utils.logs import init_loggings

LOG_LEVEL = None  # "WARN"
init_loggings(log_level=LOG_LEVEL)
