import streamlit as st

from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.ui.headers import write_header  # , write_subheader

from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import (
    get_team_from_players_name,
    SamePlayerInOneTeamError,
)

# from padel_tracker.ui.charts import make_player_metric_history_chart

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR

write_header(st.session_state.translator("check_team"))

# Make player selectbox
form = st.form("check_team")
with form:
    _, col1, col2, _ = st.columns([1, 2, 2, 1])
    with col1:
        player1_name = st.selectbox(
            label=st.session_state.translator("player1"),
            options=st.session_state.player_names,
            placeholder="",  # st.session_state.translator("player1"),
            index=None,
        )
    with col2:
        player2_name = st.selectbox(
            label=st.session_state.translator("player2"),
            options=st.session_state.player_names,
            placeholder="",
            index=None,
        )
    _, col_center, _ = st.columns([1, 3, 1])
    with col_center:
        submit_button = st.form_submit_button(
            label=st.session_state.translator("submit"), use_container_width=True
        )

st.write("")

is_players_all_fulfilled = True
if submit_button:
    if (not player1_name) or (not player2_name):
        st.error(st.session_state.translator("player_not_selected_error"), icon="💢")
        is_players_all_fulfilled = False

if submit_button and is_players_all_fulfilled:
    with DB.get_session() as session:
        try:
            team = get_team_from_players_name(
                session=session,
                player1_name=player1_name,
                player2_name=player2_name,
                create_if_not_found=False,
            )
        except SamePlayerInOneTeamError:
            st.error(st.session_state.translator("team_same_player_error"), icon="💢")
        except Exception as exc:
            err_msg = f"{st.session_state.translator("match_added_error")}: {exc}"
            st.error(err_msg, icon="💥")

# TODO: Get team from names
# team = pla

# TODO: Graph
# write_subheader(st.session_state.translator("evolution"))
# make_player_metric_history_chart(player_name=player_name, translator=st.session_state.translator)

# TODO: Short table (team elo, nb match, v, d, v/d) OR cool card ?

# TODO: All matches history cards as team

# TODO: Favorite victims

# TODO: Black beasts (team against lost the most)
