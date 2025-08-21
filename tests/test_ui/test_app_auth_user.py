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
    at = AppTest.from_file(APP_PATH, default_timeout=120)
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

    # TODO : add new match via the form
    ## Click "Add match button"
    ##
    print("coucou")
