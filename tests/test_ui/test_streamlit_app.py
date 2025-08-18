import pytest
from streamlit.testing.v1 import AppTest

from padel_tracker.utils.paths import APP_PATH
from tests.conftest import TEST_DUMMY_PLAYER_NAMES


@pytest.mark.ui
def test_app_launch_as_guest(populate_db):
    # Populate db with 2 leagues
    populate_db(
        league_name="Yatta League", player_names=TEST_DUMMY_PLAYER_NAMES, nb_matches=4
    )
    populate_db(
        league_name="Another league",
        player_names=["Oui", "Sissi", "No", "Blbl"],
        nb_matches=2,
    )
    # Launch App
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

    # Check page overview
    ##TODO : check billboard chart
    print(at)
    ##TODO : check players table (dataframe)

    ##TODO : check match list

    # Check "check player" page
    ## Click on button from Overview
    button_check_player = None
    for button in at.button:
        if translator("check_player") == button.label:
            button_check_player = button
    assert button_check_player is not None
    button_check_player.click().run()
    ##TODO : Select player
    ##TODO (prio 2) : Check basic stuff
    print(at)
