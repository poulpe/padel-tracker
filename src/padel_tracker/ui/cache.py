import streamlit as st

from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, match_manager, ranking_manager


def update_cache(force: bool = False):
    if ("df_players" not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state.df_players = player_manager.get_all_players(
                session=session, as_df=True
            )
        st.session_state.player_names = list(st.session_state.df_players["name"])
    if ("df_matches" not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state.df_matches = match_manager.get_all_matches(
                session=session, as_df=True
            )
    if ("df_elo_hist" not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state["df_elo_hist"] = ranking_manager.get_elo_rating_history(
                session=session, as_df=True
            )


def clear_cache():
    for element in ["df_players", "df_elo_hist"]:
        if element in st.session_state:
            st.session_state[element] = None


def refresh_cache():
    # clear_cache()
    update_cache(force=True)
