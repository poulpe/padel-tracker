import streamlit as st

from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import create_player, PlayerExistsError

FONT_SIZE_HEADER = 30
FONT_SIZE_SUBHEADER = 20

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR

st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: {FONT_SIZE_HEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("add_player")} </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True,
)

form = st.form("add_player")
with form:
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        player_name = st.text_input(st.session_state.translator("name"))
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=st.session_state.translator("submit"), use_container_width=True,
        )

if submit_button:
    with DB.get_session() as session:
        try:
            create_player(session=session, name=player_name)
            st.success(
                f"{player_name}{st.session_state.translator("player_added_success")}",
                icon="🔥",
            )
        except PlayerExistsError:
            st.error(
                f"{player_name}{st.session_state.translator("player_exists_error")}",
                icon="💢",
            )
        except Exception as exc:
            st.error(
                f"{st.session_state.translator("player_added_error")}: {exc}", icon="💥"
            )
