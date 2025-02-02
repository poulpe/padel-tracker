import streamlit as st

from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import delete_player
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.inputs import make_player_selectbox
from padel_tracker.utils.errors import PlayerNotFoundError

st.write("")

write_header(st.session_state.translator("delete_player"))

form = st.form(st.session_state.translator("delete_player"))
with form:
    player_name = make_player_selectbox()
    _, col, _ = st.columns(3)
    with col:
        submit_button = st.form_submit_button(
            st.session_state.translator("delete"), use_container_width=True
        )

if submit_button and player_name:
    with DB.get_session() as session:
        try:
            delete_player(session=session, name=player_name)
            msg = f"{player_name} {st.session_state.translator("player_deleted")}"
            st.success(msg, icon="☠️")
        except PlayerNotFoundError:
            err_msg = f"{st.session_state.translator("player_already_deleted")}"
            st.error(err_msg, icon="💥")
        except Exception as exc:
            err_msg = f"{st.session_state.translator("player_deletion_error")}: {exc}"
            st.error(err_msg, icon="💥")

    refresh_cache()
