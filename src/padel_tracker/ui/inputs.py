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
