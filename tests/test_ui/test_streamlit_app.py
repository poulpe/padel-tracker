from streamlit.testing.v1 import AppTest

from padel_tracker.utils.paths import APP_PATH


# TODO : test_app_launch
def test_app_launch():
    at = AppTest.from_file(APP_PATH, default_timeout=12)
    # Declare dummy secrets
    at.secrets["general.db_mode"] = "local"
    at.secrets["general.run_mode"] = "test"
    at.secrets["auth.redirect_uri"] = "http://localhost:8501/oauth2callback"
    at.secrets["auth.cookie_secret"] = "12"
    # Launch app
    at.run()
    # Check some data in cache
    translator = at.session_state.translator
    assert translator is not None
    # Check landing on "welcome/login" page
    is_button_login_there = False
    button_connect_as_guest = None
    for button in at.button:
        if translator("login_signup") == button.label:
            is_button_login_there = True
        elif translator("connect_as_guest") == button.label:
            button_connect_as_guest = button
    assert is_button_login_there
    assert button_connect_as_guest is not None
    # Enter as Guest
    button_connect_as_guest.click().run()
    # print(at)
