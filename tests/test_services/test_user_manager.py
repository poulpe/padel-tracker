import pytest

from padel_tracker.utils.errors import UserExistsError
from padel_tracker.database.db import commit_to_db
from padel_tracker.models.users import UserRole
from padel_tracker.services import user_manager


def test_create_get_delete_user_with_player(
    db_session, make_dummy_player, make_dummy_league, make_dummy_user
):
    # Prepare test
    league_name = "Hello la Liga"
    league = make_dummy_league(league_name)

    # Create user with player
    user_name = "NewUser NewPlayer"
    user = make_dummy_user(
        user_name, default_league_name=league_name, is_create_player=True
    )
    assert user.name == user_name
    assert user.player.name == user_name
    assert user.player.nb_matches == 0
    assert user.player_id == user.player.id
    assert user.default_league_name == league_name
    assert user.nb_visits == 1
    # Check error raised when recreating same user
    with pytest.raises(UserExistsError):
        user_manager.create_user_from_auth_user(
            db_session,
            dict_auth_user={"sub": user.auth_user_id, "name": user_name},
            is_create_player=False,
        )

    # Create user without player
    user_name = "NewUser NoPlayer"
    user = make_dummy_user(
        user_name, default_league_name=league_name, is_create_player=False
    )
    auth_user_id = user.auth_user_id
    ## Get user and update
    with db_session as session:
        user = user_manager.get_user_from_auth_user_id(session, auth_user_id)
        new_player = make_dummy_player(user_name, league=league)
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
