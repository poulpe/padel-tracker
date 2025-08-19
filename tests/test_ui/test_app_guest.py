import pytest
from streamlit.testing.v1 import AppTest

from padel_tracker.utils.paths import APP_PATH
from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.ranking import ELO_BASE_RATING
from padel_tracker.services import player_manager
from tests.conftest import TEST_DUMMY_PLAYER_NAMES


@pytest.mark.ui
def test_app_as_guest(db_session, populate_db, make_dummy_event):
    # Populate db with 2 leagues
    populate_db(
        league_name="MegaPro Liga", player_names=TEST_DUMMY_PLAYER_NAMES, nb_matches=4
    )
    populate_db(
        league_name="Another league",
        player_names=["Oui", "Sissi", "No", "Blbl"],
        nb_matches=2,
    )
    make_dummy_event("S1 start", date=now(), category="season_reset")
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
    ## Check billboard chart
    ### Find chart element
    chart_element = None
    for idx, el in at.main.children.items():
        if el.type == "arrow_vega_lite_chart":
            chart_element = el
            break
    assert chart_element is not None
    ### Check click on 'temporal_time_scale' button
    time_scale_toggle_button = None
    for button in at.toggle:
        if translator("time_scale") in button.label:
            time_scale_toggle_button = button
            break
    assert time_scale_toggle_button is not None
    time_scale_toggle_button.set_value(True).run()
    ## Check players table (dataframe)
    df_table = at.dataframe.values[0]
    assert not df_table.empty
    for col in ["name", "elo_rating", "rank", "nb_matches", "nb_victories"]:
        assert translator(col) in df_table.columns
    for player_name in TEST_DUMMY_PLAYER_NAMES:
        assert player_name in df_table[translator("name")].values
    assert df_table[translator("elo_rating")].max() > ELO_BASE_RATING
    assert df_table[translator("elo_rating")].min() < ELO_BASE_RATING
    ## TODO : check match list

    # Check "check player" page
    ## Prepare session state to trick the system (streamlit limitation...)
    df_top_player = df_table.query(f"{translator("rank")} == 1").reset_index()
    top_player_name = df_top_player.at[0, translator("name")]
    top_player_id = player_manager.get_player_from_name(db_session, top_player_name).id
    at.session_state["user"] = {
        "auth_user_id": "auth666x69",
        "player_id": top_player_id,
        "name": top_player_name,
    }
    ## Click on button from Overview
    button_check_player = None
    for button in at.button:
        if translator("check_player") == button.label:
            button_check_player = button
    assert button_check_player is not None
    button_check_player.click().run()  # at.switch_page("page_check_player.py").run()
    ## Check "Select player" is there
    select_player_box = None
    for box in at.main.selectbox:
        if box.label == translator("player"):
            select_player_box = box
    assert select_player_box is not None
    ##TODO (prio 2) : Check basic
    ###TODO:  Click on all metrics buttons
    # at.main.button_group[0].set_value([translator("rank")]).run()
    # button_check_player.click().run()

    # TODO: Check "check team" page
    # at.switch_page("page_check_team.py").run()
