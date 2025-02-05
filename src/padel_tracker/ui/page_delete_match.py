import streamlit as st

from padel_tracker.database.db import DB
from padel_tracker.services.match_manager import delete_match
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header

# from padel_tracker.ui.inputs import make_match_selectbox
from padel_tracker.utils.errors import PlayerNotFoundError

st.write("")

write_header(st.session_state.translator("delete_match"))

# TODO : UI to fetch match to delete
# Match is: players,
st.write("TODO, SOON")
st.stop()

form = st.form(st.session_state.translator("delete_match"))
with form:
    match_id = 12  # = make_match_selectbox()
    _, col, _ = st.columns(3)
    with col:
        submit_button = st.form_submit_button(
            st.session_state.translator("delete"), use_container_width=True
        )

if submit_button and match_id:
    with DB.get_session() as session:
        try:
            delete_match(session=session, match_id=match_id)
            msg = f"{match_id} {st.session_state.translator("match_deleted")}"
            st.success(msg, icon="☠️")
        except PlayerNotFoundError:
            err_msg = f"{st.session_state.translator("match_already_deleted")}"
            st.error(err_msg, icon="💥")
        except Exception as exc:
            err_msg = f"{st.session_state.translator("match_deletion_error")}: {exc}"
            st.error(err_msg, icon="💥")

    refresh_cache()
