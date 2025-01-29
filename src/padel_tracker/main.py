import subprocess

# Must keep this line below to init all SQLModel defined
from padel_tracker import models as models
from padel_tracker.utils.logs import init_loggings
from padel_tracker.database.db import init_db_and_tables
from padel_tracker.utils.paths import get_absolute_path


def init_app(log_level_console: str | int = None) -> None:
    """Init logs + create database tables if they don't exist"""
    init_loggings(log_level_console=log_level_console)
    init_db_and_tables()


def run_streamlit_app() -> None:
    app_path = get_absolute_path(__file__, "./ui/streamlit_app.py")
    subprocess.run(["streamlit", "run", str(app_path)])


if __name__ == "__main__":
    # init_app() is already called in streamlit app, no needs to recall it
    run_streamlit_app()
