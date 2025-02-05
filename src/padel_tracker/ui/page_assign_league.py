import streamlit as st

from padel_tracker.utils.errors import PlayerAlreadyInLeagueError
from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.ui.inputs import make_player_selectbox, make_league_selectbox

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

write_header(translator("assign_league"))

form = st.form("assign_league")
with form:
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        league_name = make_league_selectbox()
        player_name = make_player_selectbox()
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=translator("submit"),
            use_container_width=True,
        )

if submit_button:
    with DB.get_session() as session:
        try:
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
    refresh_cache()
