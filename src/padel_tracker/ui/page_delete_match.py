import streamlit as st

from padel_tracker.ui.threads import get_thread_pool
from padel_tracker.utils.errors import PlayerNotFoundError
from padel_tracker.database.db import DB
from padel_tracker.services.match_manager import delete_match
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import get_translator

# from padel_tracker.ui.inputs import make_match_selectbox

st.write("")

translator = get_translator()

write_header(translator("delete_match"))

# TODO (prio 1) : UI to fetch match to delete
# Match is: players, date/time
st.write("TODO, SOON")
# st.stop()

form = st.form(translator("delete_match"))
with form:
    match_id = st.text_input("match_id")  # 12  # = make_match_selectbox()
    _, col, _ = st.columns(3)
    with col:
        submit_button = st.form_submit_button(
            translator("delete"), use_container_width=True
        )

if submit_button and match_id:
    with DB.get_session() as session:
        try:
            delete_match(
                session=session, match_id=match_id, thread_pool=get_thread_pool()
            )
            st.success(f"{translator('match_deleted')} (id={match_id} )", icon="☠️")
        except PlayerNotFoundError:
            st.error(f"{translator('match_already_deleted')}", icon="💥")
        except Exception as exc:
            st.error(f"{translator('match_deletion_error')}: {exc}", icon="💥")
    refresh_cache(threaded=True)
