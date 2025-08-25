import pytest
from streamlit.testing.v1 import AppTest

from padel_tracker.utils.paths import APP_PATH
from padel_tracker.utils.datetime_utils import now
from padel_tracker.services import player_manager, match_manager, event_manager
from tests.conftest import TEST_DUMMY_PLAYER_NAMES


@pytest.mark.ui
def test_page_check_team(db_session, populate_db, make_dummy_event):
    # Populate db with leagues
    league_name = "MegaPro Liga"
    populate_db(
        league_name=league_name, player_names=TEST_DUMMY_PLAYER_NAMES, nb_matches=4
    )
    make_dummy_event("S1 start", date=now(), category="season_reset")
    ## Find team that has match history
    df_teams = player_manager.get_all_teams_from_league(
        session=db_session,
        league_name=league_name,
        as_df=True,
    )
    df_teams_filtered = df_teams.query("nb_matches>0").copy()
    test_team_name = df_teams_filtered.at[0, "name"]
    test_p1_name, test_p2_name = test_team_name.split("/")

    # Prepare App
    at = AppTest.from_file(APP_PATH.parent / "page_check_team.py", default_timeout=30)
    at.session_state["league_name"] = league_name
    players = player_manager.get_all_players_from_league(db_session, league_name)
    at.session_state["player_names"] = [p.name for p in players]
    at.session_state["df_teams"] = df_teams.copy()
    at.session_state["df_matches"] = match_manager.get_all_matches_from_league(
        session=db_session,
        as_df=True,
        league_name=league_name,
    )
    at.session_state["df_events"] = event_manager.get_all_events_from_league(
        session=db_session,
        as_df=True,
        league_name=league_name,
    )
    at.run()
    translator = at.session_state.translator

    # Select team
    for box in at.main.selectbox:
        if box.label == translator("player1"):
            updated_box = box.select(test_p1_name)
            assert updated_box.value == test_p1_name
        elif box.label == translator("player2"):
            updated_box = box.select(test_p2_name)
            assert updated_box.value == test_p2_name
    # Click submit
    button_submit = None
    for button in at.main.button:
        if button.label == translator("submit"):
            button_submit = button
            break
    assert button_submit is not None
    button_submit.click().run()

    # TODO (prio 3) : Check stuff
