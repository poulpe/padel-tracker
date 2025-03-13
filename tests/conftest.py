import pytest

# from padel_tracker.utils.conf import DBMode, RunMode
from padel_tracker.utils.paths import APP_PATH as APP_PATH
from padel_tracker.database.db import DB, init_db_and_tables

# Database


@pytest.fixture
def db_session():
    init_db_and_tables(DB)
    session = DB.get_session()
    yield session
    session.close()


# Dummy names
TEST_LEAGUE_NAME = "Liga Demo"
TEST_P1_NAME = "ElTrueno"
TEST_P2_NAME = "Raqueta Loca"
TEST_P3_NAME = "LaBiba"
TEST_P4_NAME = "Chaco Smash"

# UI
