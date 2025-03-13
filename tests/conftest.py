import pytest

from padel_tracker.utils.conf import DBMode, RunMode
from padel_tracker.database.db import Database, init_db_and_tables

DB_TEST = Database(
    db_mode=DBMode.LOCAL,
    run_mode=RunMode.TEST,
)


@pytest.fixture
def db_session():
    init_db_and_tables(DB_TEST)
    session = DB_TEST.get_session()
    yield session
    session.close()
