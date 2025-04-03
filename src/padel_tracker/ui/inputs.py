import streamlit as st

from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import get_all_players_names


def make_player_selectbox(player_name: str = None, all_leagues: bool = False) -> str:
    index = None
    if all_leagues:
        with DB.get_session() as session:
            player_names = get_all_players_names(session=session)
    else:
        player_names = st.session_state.player_names
    if player_name:
        try:
            index = player_names.index(player_name)
        except ValueError:
            index = None

    player_name = st.selectbox(
        label=st.session_state.translator("player_name"),
        options=player_names,
        placeholder=st.session_state.translator("player"),
        index=index,
    )
    return player_name


def make_league_selectbox(league_name: str = None) -> str:
    index = None
    if league_name:
        try:
            index = st.session_state.league_names.index(league_name)
        except ValueError:
            index = None
    league_name = st.selectbox(
        label=st.session_state.translator("league_name"),
        options=st.session_state.league_names,
        placeholder=st.session_state.translator("league"),
        index=index,
    )
    return league_name


# def scale_max_league_name_length(x:float)->float:
#     return -2E-05*x**4 + 0.0032*x**3 - 0.2122*x**2 + 6.2259*x + 6
#
# def make_league_selectbox():
#     len_league_name = len(st.session_state.league_name)
#     max = scale_max_league_name_length(len_league_name)
#
#     _, col_center, _ = st.columns(
#         [(max-len_league_name)/2, len_league_name, (max-len_league_name)/2]
#     )
#     with col_center:
#         st.selectbox(
#             st.session_state.translator("league"),
#             st.session_state.league_names,
#             key="league_name",
#             label_visibility="hidden",
#             on_change=update_cache,
#             kwargs={"force":True},
#
#         )
