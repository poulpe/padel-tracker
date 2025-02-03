import os
from enum import StrEnum
from typing import Any

from dotenv import load_dotenv
import streamlit as st


class DBMode(StrEnum):
    LOCAL = "local"
    CLOUD = "cloud"


class RunMode(StrEnum):
    TEST = "test"
    PROD = "prod"


def get_conf() -> dict[str, Any]:
    """Get conf in this order: try from dotenv first, else try from st.secrets
    Fallback to None if not found.
    """
    dict_conf = {}
    dict_conf["db_credentials"] = {}
    dict_conf["general"] = {}

    db_keys = [
        "user",
        "password",
        "host",
        "port",
        "dbname",
        "supabase_api_url",
        "supabase_api_key",
    ]
    conf_keys = ["log_level_console", "db_mode", "run_mode"]

    load_dotenv()

    ## db stuff
    for key in db_keys:
        value = os.getenv(key)
        if value is None:
            try:
                value = st.secrets["db_credentials"][key]
            except KeyError:
                pass
        dict_conf["db_credentials"][key] = value
    ## General conf
    for key in conf_keys:
        value = os.getenv(key)
        if value is None:
            try:
                value = st.secrets["general"][key]
            except KeyError:
                pass
        dict_conf["general"][key] = value

    return dict_conf


DICT_CONF = get_conf()
