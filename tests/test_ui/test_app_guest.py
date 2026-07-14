import pytest
from streamlit.testing.v1 import AppTest

from padel_tracker.utils.paths import APP_PATH
from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.ranking import ELO_BASE_RATING
from padel_tracker.services import player_manager, match_manager, event_manager
from tests.conftest import TEST_DUMMY_PLAYER_NAMES, find_st_object


@pytest.mark.ui
def test_app_as_guest(db_session, populate_db, make_dummy_event, make_dummy_user):
    """
    Notes
    -----
    Cannot test mutllpage/navigation app yet from Streamlit limit (Aug 2025 with v1.48)
    Typically at.switch_page("page_two.py").run() doesn't work
    """
    # Populate db with 2 leagues
    main_league_name = "MegaPro Liga"
    populate_db(
        league_name=main_league_name, player_names=TEST_DUMMY_PLAYER_NAMES, nb_matches=4
    )
    populate_db(
        league_name="Another league",
        player_names=["Coucou", "Yorg", "Bautista Sanchez", "Weeman"],
        nb_matches=2,
    )
    make_dummy_event("S1 start", date=now(), category="season_reset")
    # Launch App
    at = AppTest.from_file(APP_PATH, default_timeout=12)
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
        if el.type == "vega_lite_chart":
            chart_element = el
            break
    assert chart_element is not None
    ### Check click on 'temporal_time_scale' button
    time_scale_toggle_button = find_st_object(at.toggle, translator("time_scale"))
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
    button_check_player = find_st_object(at.button, translator("check_player"))
    button_check_player.click().run()
    ## Check "Select player" is there
    find_st_object(at.main.selectbox, translator("player"))

    # Check "check team" page
    ## Find team that has match history
    df_teams = player_manager.get_all_teams_from_league(
        session=db_session,
        league_name=main_league_name,
        as_df=True,
    )
    df_teams_filtered = df_teams.query("nb_matches>0").copy()
    test_team_name = df_teams_filtered.at[0, "name"]
    test_p1_name, test_p2_name = test_team_name.split("/")
    ## Simulate App clicked from navigation
    at2 = AppTest.from_file(APP_PATH.parent / "page_check_team.py", default_timeout=12)
    at2.session_state["league_name"] = main_league_name
    players = player_manager.get_all_players_from_league(db_session, main_league_name)
    at2.session_state["player_names"] = [p.name for p in players]
    at2.session_state["df_teams"] = df_teams.copy()
    at2.session_state["df_matches"] = match_manager.get_all_matches_from_league(
        session=db_session,
        as_df=True,
        league_name=main_league_name,
    )
    at2.session_state["df_events"] = event_manager.get_all_events_from_league(
        session=db_session,
        as_df=True,
        league_name=main_league_name,
    )
    at2.run()
    translator = at2.session_state.translator
    ## Select team
    for box in at2.main.selectbox:
        if box.label == translator("player1"):
            updated_box = box.select(test_p1_name)
            assert updated_box.value == test_p1_name
        elif box.label == translator("player2"):
            updated_box = box.select(test_p2_name)
            assert updated_box.value == test_p2_name
    ## Click submit
    button_submit = find_st_object(at2.main.button, translator("submit"))
    button_submit.click().run()
    ## TODO (st limit) : Check click on metric button
    # metric_button = None
    # for button_group in at.main.button_group:
    #     if button_group.proto.label == translator("metric"):
    #         metric_button = button_group
    #         break
    # assert metric_button is not None
    # metric_button.select(translator("nb_won_games_diff")).run()
    ## TODO (prio 3) : Check other elements on page check team
