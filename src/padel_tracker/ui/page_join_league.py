import streamlit as st

from padel_tracker.utils.errors import PlayerAlreadyInLeagueError
from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import get_translator
from padel_tracker.ui.inputs import make_league_selectbox

st.write("")

translator = get_translator()

write_header(translator("join_league"))

form = st.form("join_league")
with form:
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        league_name = make_league_selectbox()
        # player_name = make_player_selectbox(all_leagues=True)
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=translator("submit"),
            width="stretch",
        )

if submit_button:
    player_name = st.session_state.user["name"]
    try:
        with DB.get_session() as session:
            player = player_manager.get_player_from_name(
                session=session, name=player_name
            )
            league = league_manager.get_league_from_name(
                session=session, name=league_name
            )
            league_manager.assign_league_to_player(
                session=session, player=player, league=league
            )
        st.success(
            f"{player_name}{translator("assigned_league_to_player_success")}{league_name}",
            icon="🔥",
        )
    except PlayerAlreadyInLeagueError:
        st.error(
            f"{player_name}{translator("player_already_in_league_error")}{league_name}",
            icon="💢",
        )
    except Exception as exc:
        st.error(f"{translator("player_added_error")}: {exc}", icon="💥")
    else:
        refresh_cache(threaded=True)
