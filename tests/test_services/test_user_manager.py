from tests.conftest import TEST_P1_NAME, TEST_LEAGUE_NAME
from padel_tracker.utils.errors import UserExistsError
from padel_tracker.services import user_manager


def test_create_get_user(db_session):
    auth_user_id = "auth123"
    user_name = TEST_P1_NAME
    dict_auth_user = {"sub": auth_user_id, "name": user_name}
    try:
        user = user_manager.create_user_from_auth_user(
            db_session,
            dict_auth_user=dict_auth_user,
            is_create_player=False,
            default_league_name=TEST_LEAGUE_NAME,
        )
    except UserExistsError:
        user = user_manager.get_user_from_auth_user_id(db_session, auth_user_id)
    assert user.auth_user_id == auth_user_id
    assert user.name == user_name
    assert user.default_league_name == TEST_LEAGUE_NAME
