import streamlit as st

from padel_tracker.utils.errors import PlayerExistsError, InvalidPlayerNameError
from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

write_header(translator("add_player"))

form = st.form("add_player")
with form:
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        player_name = st.text_input(translator("name"))
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=translator("submit"),
            use_container_width=True,
        )

if submit_button:
    with DB.get_session() as session:
        try:
            # Fetch league
            league = league_manager.get_league_from_name(
                session=session, name=st.session_state.league_name
            )
            player_manager.create_player(
                session=session, name=player_name, league=league
            )
            st.success(f"{player_name}{translator("player_added_success")}", icon="🔥")
        except PlayerExistsError:
            st.error(
                f"{player_name}{translator("player_exists_error")}",
                icon="💢",
            )
        except InvalidPlayerNameError:
            st.error(
                f"{player_name}{translator("player_invalid_name_error")}",
                icon="💢",
            )
        except Exception as exc:
            st.error(f"{translator("player_added_error")}: {exc}", icon="💥")
    refresh_cache()
