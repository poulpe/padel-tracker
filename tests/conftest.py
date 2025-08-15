from datetime import datetime

import pytest

from padel_tracker.utils.conf import DBMode, RunMode
from padel_tracker.utils.errors import (
    UserExistsError,
    PlayerExistsError,
    LeagueExistsError,
    MatchExistsError,
)
from padel_tracker.models.leagues import League
from padel_tracker.models.players import Player, Team
from padel_tracker.models.users import User
from padel_tracker.models.matches import Match
from padel_tracker.models.events import Event
from padel_tracker.database.db import Database, init_db_and_tables
from padel_tracker.services import (
    user_manager,
    player_manager,
    league_manager,
    match_manager,
    event_manager,
)

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
    created_league_names = []

    def _factory(name: str, is_private: bool = False, admin_name: str = "") -> League:
        # Create it, otherwise fetch it
        try:
            league = league_manager.create_league(
                db_session, name=name, is_private=is_private, admin_name=admin_name
            )
            created_league_names.append(name)
        except LeagueExistsError:
            league = league_manager.get_league_from_name(db_session, name=name)
        return league

    # Yield
    yield _factory

    # Delete
    for name in created_league_names:
        league_manager.delete_league(db_session, name=name)


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
    created_player_names = []

    def _factory(name: str, league: League | list[League] | None = None) -> Player:
        # Create it, otherwise fetch it
        try:
            player = player_manager.create_player(db_session, name=name, league=league)
            created_player_names.append(name)
        except PlayerExistsError:
            player = player_manager.get_player_from_name(db_session, name=name)
        return player

    # Yield
    yield _factory

    # Delete
    for name in created_player_names:
        player_manager.delete_player(db_session, name=name)


@pytest.fixture
def make_dummy_team(db_session):
    """
    Create dummy team with given player names (or fetch if already existing)
    and then make sure it's deleted at the end of the test

    Examples
    --------
    >>> def test_make_dummy_team(make_dummy_team):
    ...     p1_name = "Oui"
    ...     p2_name = "Muchacho"
    ...     team = make_dummy_team(p1_name, p2_name, league_name="Daliga")
    ...     assert p1_name in team.name
    """
    created_team_player_names = []  # As a tuple (p1_name, p2_name)

    def _factory(player1_name: str, player2_name: str, league_name: str = None) -> Team:
        # Create it, otherwise fetch it
        created_team_player_names.append((player1_name, player2_name))
        return player_manager.get_team_from_players_name(
            db_session,
            player1_name,
            player2_name,
            league_name,
            create_if_not_found=True,
        )

    # Yield
    yield _factory

    # Delete
    for names in created_team_player_names:
        player_manager.delete_team(
            db_session, player1_name=names[0], player2_name=names[1]
        )


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
    # Register dict {"user_name": is_player_created}
    dict_created_user_names: dict[str, bool] = {}

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
            dict_created_user_names[name] = is_create_player
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
            dict_created_user_names[name] = False
        return user

    # Yield
    yield _factory

    # Delete
    for name, was_player_created in dict_created_user_names.items():
        user_manager.delete_user(db_session, name=name)
        if was_player_created:
            player_manager.delete_player(db_session, name)


## match_manager
@pytest.fixture
def make_dummy_match(db_session, make_dummy_league, make_dummy_player, make_dummy_team):
    """
    Create dummy match with given name (or fetch if already existing) and then make sure
    it's deleted at the end of the test

    Examples
    --------
    >>> def test_make_dummy_match(make_dummy_match):
    ...     # Make a date
    ...     date = make_datetime(day=5, month=2, year=2025, hour=19, minute=30)
    ...     # Go
    ...     match = make_dummy_match(
    ...         team1_player1_name="Agustin Tapas",
    ...         team1_player2_name="Martin Di Neuneu",
    ...         team2_player1_name="Juan Cabron",
    ...         team2_player2_name="Ale Gralan",
    ...         league_name = "Mucho Pro League",
    ...         date = date,
    ...         score = "6-2, 7-6",
    ...     )
    ...     assert match.team1_won
    """
    created_match_ids = []

    def _factory(
        team1_player1_name: str,
        team1_player2_name: str,
        team2_player1_name: str,
        team2_player2_name: str,
        score: str,
        date: datetime,
        league_name: str,
        is_finished: bool = True,
        is_friendly: bool = False,
    ) -> Match:
        # Fetch league
        league = make_dummy_league(name=league_name)
        # Fetch players
        make_dummy_player(name=team1_player1_name, league=league)
        make_dummy_player(name=team1_player2_name, league=league)
        make_dummy_player(name=team2_player1_name, league=league)
        make_dummy_player(name=team2_player2_name, league=league)
        # Fetch team
        team1 = make_dummy_team(team1_player1_name, team1_player2_name, league_name)
        team2 = make_dummy_team(team2_player1_name, team2_player2_name, league_name)
        # Create it, otherwise fetch it
        try:
            match = match_manager.create_match(
                session=db_session,
                teams=[team1, team2],
                league_name=league_name,
                date=date,
                score=score,
                is_finished=is_finished,
                is_friendly=is_friendly,
            )
            created_match_ids.append(match.id)
        except MatchExistsError:
            match = match_manager.get_match(
                db_session, teams=[team1, team2], league_name=league_name, date=date
            )
        return match

    # Yield
    yield _factory

    # Delete
    for id in created_match_ids:
        match_manager.delete_match(db_session, match_id=id)


## event_manager
@pytest.fixture
def make_dummy_event(db_session):
    """
    Create dummy event with given name (or fetch if already existing)
    and then make sure it's deleted at the end of the test
    """
    created_event_ids = []

    def _factory(
        name: str,
        date: datetime,
        category: str = None,
        description: str = "",
        end_date: datetime = None,
        league_name: str = "",
    ) -> Event:
        # Create it (not implemented get_event yet...)
        event = event_manager.create_event(
            db_session,
            name=name,
            date=date,
            category=category,
            description=description,
            end_date=end_date,
            league_name=league_name,
        )
        created_event_ids.append(event.id)
        return event

    # Yield
    yield _factory

    # Delete
    for id in created_event_ids:
        event_manager.delete_event(db_session, event_id=id)


## Cross services
# TODO : populate_db
def populate_db(
    league_name: str,
    player_names: list[str],
    nb_matches: int = 10,
):
    """Populate the db with and `nb_matches` random matches between players"""
    pass
