import streamlit as st

from padel_tracker.utils.errors import LeagueExistsError, InvalidLeagueNameError
from padel_tracker.database.db import DB
from padel_tracker.services import league_manager
from padel_tracker.ui.cache import refresh_cache, force_league_name_refresh
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.languages import get_translator

st.write("")

translator = get_translator()

write_header(translator("add_league"))
write_subheader(translator("add_league_long_message"), bold=False)

form = st.form("add_league")
with form:
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        league_name = st.text_input(translator("name"))
        league_description = st.text_area(translator("description"))
    _, center_col, _ = st.columns([1.3, 1, 1])
    with center_col:
        is_private = st.checkbox(
            translator("private_league"), help=translator("private_league_help")
        )
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=translator("submit"),
            use_container_width=True,
        )

if submit_button:
    try:
        # Fetch current user to put it as league admin
        admin_name = None
        if "user" in st.session_state:
            admin_name = st.session_state.user["name"]
        # Go create
        with DB.get_session() as session:
            league = league_manager.create_league(
                session=session,
                name=league_name,
                is_private=is_private,
                admin_name=admin_name,
                description=league_description,
            )
        st.success(f"{league_name}{translator("league_added_success")}", icon="🔥")
    except LeagueExistsError:
        st.error(f"{league_name}{translator("league_exists_error")}", icon="💢")
    except InvalidLeagueNameError:
        st.error(f"{league_name}{translator("league_invalid_name_error")}", icon="💢")
    except Exception as exc:
        st.error(f"{translator("league_added_error")}: {exc}", icon="💥")
    else:
        refresh_cache(threaded=True)
        force_league_name_refresh(league_name)
