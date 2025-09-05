import os
from enum import StrEnum
from typing import Any

from dotenv import load_dotenv
import streamlit as st


class DBMode(StrEnum):
    LOCAL = "local"
    CLOUD = "cloud"


class RunMode(StrEnum):
    DEBUG = "debug"
    TEST = "test"
    PROD = "prod"


_DEFAULT_CONF = {
    "log_level_console": "INFO",
    "log_level_db": "SUCCESS",
    "db_mode": "local",
    "run_mode": "test",
}


def get_conf() -> dict[str, Any]:
    """Get conf in this order: try from dotenv first, else try from st.secrets
    Fallback to _DEFAULT_CONF if not found.
    """
    dict_conf = {}
    dict_conf["general"] = {}
    dict_conf["db_credentials"] = {}

    conf_keys = ["db_mode", "run_mode", "log_level_console", "log_level_db"]
    db_keys = ["db_url_cloud"]

    load_dotenv()

    # General conf
    for key in conf_keys:
        value = os.getenv(key)
        if value is None:
            try:
                value = st.secrets["general"][key]
            except (KeyError, FileNotFoundError):
                value = _DEFAULT_CONF[key]
        dict_conf["general"][key] = value
    ## Check modes are valid
    db_mode_lowercase = dict_conf["general"]["db_mode"].lower()
    dict_conf["general"]["db_mode"] = DBMode(db_mode_lowercase).value
    run_mode_lowercase = dict_conf["general"]["run_mode"].lower()
    dict_conf["general"]["run_mode"] = RunMode(run_mode_lowercase).value

    # db stuff
    for general_key in db_keys:
        specific_key = f"{general_key}_{dict_conf["general"]["run_mode"]}"
        value = os.getenv(specific_key)
        if value is None:
            try:
                value = st.secrets["db_credentials"][specific_key]
            except (KeyError, FileNotFoundError):
                pass
        dict_conf["db_credentials"][general_key] = value

    return dict_conf


DICT_CONF = get_conf()


def is_test_mode() -> bool:
    return DICT_CONF["general"]["run_mode"] == RunMode.TEST.value


def get_conf_message() -> str:
    """Returns string with main parameters deducted from conf to init the app"""
    log_level_console = DICT_CONF["general"]["log_level_console"]
    log_level_db = DICT_CONF["general"]["log_level_db"]
    db_mode = DBMode(DICT_CONF["general"]["db_mode"].lower())
    run_mode = RunMode(DICT_CONF["general"]["run_mode"].lower())
    return f"db_mode={str(db_mode)}, run_mode={str(run_mode)}, {log_level_console=}, {log_level_db=}"
