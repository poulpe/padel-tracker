from datetime import date, time
import pytest
from streamlit.testing.v1 import AppTest

from padel_tracker.utils.paths import APP_PATH
from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.users import UserRole
from padel_tracker.services import player_manager, user_manager
from tests.conftest import TEST_DUMMY_PLAYER_NAMES


# TODO (prio1) : test app as auth user
@pytest.mark.ui
def test_app_as_exiting_auth_user(
    db_session, populate_db, make_dummy_user, make_dummy_event
):
    # Populate db with leagues + user
    league_name = "MegaPro Liga"
    populate_db(
        league_name=league_name, player_names=TEST_DUMMY_PLAYER_NAMES, nb_matches=4
    )
    make_dummy_event("S1 start", date=now(), category="season_reset")
    ## Find top player (to make sure it has match history) and create associated user
    df_players = player_manager.get_all_players_from_league(
        session=db_session,
        league_name=league_name,
        as_df=True,
    )
    df_players = df_players.sort_values(by="elo_rating", ascending=False).reset_index()
    top_player_name = df_players.at[0, "name"]
    top_player = player_manager.get_player_from_name(db_session, top_player_name)
    top_user = make_dummy_user(
        name=top_player_name, default_league_name=league_name, is_create_player=False
    )
    user_manager.assign_player_to_user(db_session, top_user, top_player)

    # Prepare app
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    ## Declare dummy secrets
    at.secrets["auth.redirect_uri"] = "http://localhost:8501/oauth2callback"
    at.secrets["auth.cookie_secret"] = "12"
    ## Simulate logged user from the auth
    at.session_state["user"] = top_user.model_dump()
    at.session_state["user"]["admin_leagues"] = [
        league.name for league in top_user.admin_leagues
    ]
    at.session_state["user"]["is_logged_in"] = True
    at.session_state["user"]["role"] = UserRole.TRUSTEDPLAYER

    # Launch app
    at.run()
    translator = at.session_state.translator
    assert translator is not None
    player_names = at.session_state["player_names"]
    assert top_player_name in player_names

    # Add new match via the form
    ## Click "Add match button" from overview page
    button_add_match = None
    for button in at.button:
        if button.label == translator("add_match"):
            button_add_match = button
            break
    assert button_add_match is not None
    button_add_match.click().run()
    ## Simulate page_add_match
    at2 = AppTest.from_file(APP_PATH.parent / "page_add_match.py", default_timeout=30)
    at2.session_state["player_names"] = player_names.copy()
    at2.session_state["league_name"] = league_name
    at2.run()
    translator = at2.session_state.translator

    # Test add_match_page : bad score
    ## Enter players
    t1_p1_name = t1_p2_name = t2_p1_name = t2_p2_name = None
    for box in at2.main.selectbox:
        if box.key == "add_match_t1_p1":
            updated_box = box.select_index(2)
            t1_p1_name = updated_box.value
        elif box.key == "add_match_t1_p2":
            updated_box = box.select_index(1)
            t1_p2_name = updated_box.value
        elif box.key == "add_match_t2_p1":
            updated_box = box.select_index(3)
            t2_p1_name = updated_box.value
        elif box.key == "add_match_t2_p2":
            updated_box = box.select_index(5)
            t2_p2_name = updated_box.value
    for name in [t1_p1_name, t1_p2_name, t2_p1_name, t2_p2_name]:
        assert name is not None
    ## TODO : Enter score (not possible to change values today, streamlit limitation)
    df_score = at2.main.dataframe[0]
    assert df_score is not None
    assert "Set1" in df_score.columns
    ## Enter datetime
    at2.main.date_input[0].set_value(date(day=26, month=8, year=2025))
    at2.main.time_input[0].set_value(time(hour=10, minute=45))
    ## Launch
    button_submit = None
    for button in at2.main.button:
        if button.label == translator("submit"):
            button_submit = button
            break
    assert button_submit is not None
    button_submit.click().run()
    ## Check "Error"
    assert len(at2.main.error) == 1
    assert at2.main.error[0].value == translator("match_not_finished_error")

    # TODO : Test add_match_page "make a OK match"
    ## Check winners/losers are coherent vs metrics
    ## Check error poping-up when reclicking on button to submit match
