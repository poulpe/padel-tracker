import pytest

from padel_tracker.utils.errors import (
    UserExistsError,
    UserNotFoundError,
    PlayerExistsError,
    LeagueNotFoundError,
    PlayerNotFoundError,
)
from padel_tracker.database.db import commit_to_db
from padel_tracker.models.users import UserRole
from padel_tracker.services import user_manager, player_manager, league_manager
from tests.conftest import TEST_LEAGUE_NAME


def test_create_get_delete_user(db_session):
    # Prepare test
    auth_user_id = "auth123"
    user_name = "NewUser"
    dict_auth_user = {"sub": auth_user_id, "name": user_name}
    # Check it doesn't exist already (and if so, delete it)
    try:
        user = user_manager.get_user_from_auth_user_id(db_session, auth_user_id)
        user_manager.delete_user(db_session, name=user.name)
    except UserNotFoundError:
        pass

    # Create user
    user = user_manager.create_user_from_auth_user(
        db_session, dict_auth_user=dict_auth_user, is_create_player=False
    )
    assert user.auth_user_id == auth_user_id
    assert user.name == user_name
    ## Check error while recreating it
    with pytest.raises(UserExistsError):
        user_manager.create_user_from_auth_user(
            db_session, dict_auth_user=dict_auth_user, is_create_player=False
        )

    # Get it and update
    with db_session as session:
        user = user_manager.get_user_from_auth_user_id(session, auth_user_id)
        ## Assert basic features with player
        try:
            new_player = player_manager.create_player(session=session, name=user_name)
        except PlayerExistsError:
            new_player = player_manager.get_player_from_name(session, user_name)
        user_manager.assign_player_to_user(session, user, new_player)
        assert user.player.name == user_name
        assert user.player.nb_matches == 0
        ## Update and check well updated
        user.nb_visits += 1
        user.role = UserRole.TRUSTEDPLAYER
        commit_to_db(user, session=session)
    with db_session as session:
        updated_user = user_manager.get_user_from_auth_user_id(session, auth_user_id)
        assert updated_user in user_manager.get_all_users(session=session)
        assert updated_user.nb_visits == 2
        assert updated_user.role == UserRole.TRUSTEDPLAYER

    # Delete
    user_manager.delete_user(session=db_session, name=user_name)
    with pytest.raises(UserNotFoundError):
        user_manager.delete_user(session=db_session, name=user_name)
    player_manager.delete_player(session=db_session, name=user_name)


def test_create_get_delete_user_with_player(db_session):
    # Prepare test
    auth_user_id = "auth666"
    user_name = "NewUser NewPlayer"
    dict_auth_user = {"sub": auth_user_id, "name": user_name}
    ## Check user doesn't exist already (and if so, delete it)
    try:
        user = user_manager.get_user_from_auth_user_id(db_session, auth_user_id)
        user_manager.delete_user(db_session, name=user.name)
    except UserNotFoundError:
        pass
    ## Check player doesn't exist already (and if so, delete it)
    try:
        player_manager.get_player_from_name(db_session, user_name)
        player_manager.delete_player(db_session, name=user_name)
    except PlayerNotFoundError:
        pass

    # Create user
    ## Ensure the league exists
    try:
        league_manager.get_league_from_name(db_session, TEST_LEAGUE_NAME)
    except LeagueNotFoundError:
        league_manager.create_league(db_session, name=TEST_LEAGUE_NAME)
    ## Go
    user = user_manager.create_user_from_auth_user(
        db_session,
        dict_auth_user=dict_auth_user,
        is_create_player=True,
        default_league_name=TEST_LEAGUE_NAME,
    )
    assert user.player.name == user_name
    assert user.player.nb_matches == 0
    assert user.player_id == user.player.id
    assert user.default_league_name == TEST_LEAGUE_NAME
    assert user.nb_visits == 1

    # Delete
    user_manager.delete_user(session=db_session, name=user_name)
    player_manager.delete_player(session=db_session, name=user_name)


def test_make_dummy_user(make_dummy_user):
    name = "Alfred"
    user = make_dummy_user(name, is_create_player=False)
    assert user.name == name
