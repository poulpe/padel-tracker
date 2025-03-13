from padel_tracker.models.users import User


def test_create_user():
    user = User(auth_user_id="auth123", name="Test User")
    assert user.auth_user_id == "auth123"
    assert user.name == "Test User"
    assert user.email is None
