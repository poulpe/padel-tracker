import subprocess

# Must keep this line below to init all SQLModel defined
from padel_tracker import models as models
from padel_tracker.utils.logs import init_loggings
from padel_tracker.database.db import init_db_and_tables
from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.utils.conf import get_conf

DICT_CONF = get_conf()


def init_app() -> None:
    init_loggings(log_level=DICT_CONF["LOG_LEVEL"])
    init_db_and_tables()


def run_streamlit_app() -> None:
    app_path = get_absolute_path(__file__, "./ui/streamlit_app.py")
    subprocess.run(["streamlit", "run", str(app_path)])


if __name__ == "__main__":
    run_streamlit_app()
