import streamlit as st

from padel_tracker.utils.errors import LeagueExistsError, InvalidLeagueNameError
from padel_tracker.database.db import DB
from padel_tracker.services import league_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

write_header(translator("add_league"))

form = st.form("add_league")
with form:
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        league_name = st.text_input(translator("name"))
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=translator("submit"),
            use_container_width=True,
        )

if submit_button:
    try:
        with DB.get_session() as session:
            league_manager.create_league(session=session, name=league_name)
        st.success(f"{league_name}{translator("league_added_success")}", icon="🔥")
    except LeagueExistsError:
        st.error(f"{league_name}{translator("league_exists_error")}", icon="💢")
    except InvalidLeagueNameError:
        st.error(f"{league_name}{translator("league_invalid_name_error")}", icon="💢")
    except Exception as exc:
        st.error(f"{translator("league_added_error")}: {exc}", icon="💥")
    else:
        refresh_cache()
