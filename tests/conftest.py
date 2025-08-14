import pytest

from padel_tracker.utils.conf import DBMode, RunMode
from padel_tracker.utils.errors import (
    UserExistsError,
    PlayerExistsError,
    LeagueExistsError,
)
from padel_tracker.models.leagues import League
from padel_tracker.models.players import Player
from padel_tracker.models.users import User
from padel_tracker.database.db import Database, init_db_and_tables
from padel_tracker.services import user_manager, player_manager, league_manager

# General const
## Dummy names
TEST_LEAGUE_NAME = "Liga Demo"
TEST_P1_NAME = "ElTrueno"
TEST_P2_NAME = "Raqueta Loca"
TEST_P3_NAME = "LaBiba"
TEST_P4_NAME = "Chaco Smash"

# Database
DB_TEST = Database(db_mode=DBMode.LOCAL, run_mode=RunMode.TEST)


@pytest.fixture
def db_session():
    init_db_and_tables(DB_TEST)
    session = DB_TEST.get_session()
    yield session
    session.close()


# Services
## user_manager
@pytest.fixture
def make_dummy_user(db_session):
    """
    Create dummy user with given name (or fetch if already existing) and then make sure
    it's deleted at the end of the test

    Examples
    --------
    >>> def test_make_dummy_user(make_dummy_user):
    ...     name = "Alfred"
    ...     user = make_dummy_user(name, is_create_player=False)
    ...     assert user.name == name
    """
    created_users = []

    def _factory(
        name: str,
        default_league_name: str | None = None,
        is_create_player: bool = False,
    ) -> User:
        # Create it, otherwise fetch it
        try:
            user = user_manager.create_user_from_auth_user(
                db_session,
                dict_auth_user={"name": name, "sub": f"auth666-{name}"},
                default_league_name=default_league_name,
                is_create_player=is_create_player,
            )
        except UserExistsError:
            user = user_manager.get_user_from_name(db_session, name=name)
            if default_league_name:
                default_league = league_manager.get_league_from_name(
                    db_session, name=default_league_name
                )
                league_manager.assign_admin_to_league(
                    db_session, user=user, league=default_league
                )
        except PlayerExistsError:
            user = user_manager.create_user_from_auth_user(
                db_session,
                dict_auth_user={"name": name, "sub": f"auth666-{name}"},
                default_league_name=default_league_name,
                is_create_player=False,
            )
        return user

    # Yield
    yield _factory

    # Delete
    for name in created_users:
        user_manager.delete_user(db_session, name=name)


## player_manager
@pytest.fixture
def make_dummy_player(db_session):
    """
    Create dummy player with given name (or fetch if already existing) and then make sure
    it's deleted at the end of the test

    Examples
    --------
    >>> def test_make_dummy_player(make_dummy_player):
    ...     my_league = "call stuff to fetch the league"
    ...     name = "Alfred"
    ...     player = make_dummy_player(name, league=my_league)
    ...     assert player.name == name
    """
    created_players = []

    def _factory(name: str, league: League | list[League] | None = None) -> Player:
        # Create it, otherwise fetch it
        try:
            player = player_manager.create_player(db_session, name=name, league=league)
        except PlayerExistsError:
            player = player_manager.get_player_from_name(db_session, name=name)
        return player

    # Yield
    yield _factory

    # Delete
    for name in created_players:
        player_manager.delete_player(db_session, name=name)


## league_manager
@pytest.fixture
def make_dummy_league(db_session):
    """
    Create dummy league with given name (or fetch if already existing) and then make sure
    it's deleted at the end of the test

    Examples
    --------
    >>> def test_make_dummy_league(make_dummy_league):
    ...     name = "Mucho liga"
    ...     league = make_dummy_league(name=name, is_private=True, admin_name="DaChef")
    ...     assert league.name == name
    """
    created_leagues = []

    def _factory(name: str, is_private: bool = False, admin_name: str = "") -> League:
        # Create it, otherwise fetch it
        try:
            league = league_manager.create_league(
                db_session, name=name, is_private=is_private, admin_name=admin_name
            )
        except LeagueExistsError:
            league = league_manager.get_league_from_name(db_session, name=name)
        return league

    # Yield
    yield _factory

    # Delete
    for name in created_leagues:
        league_manager.delete_league(db_session, name=name)
