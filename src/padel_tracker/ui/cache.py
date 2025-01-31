import streamlit as st

from padel_tracker.database.db import DB
from padel_tracker.utils.logs import get_logger
from padel_tracker.services import player_manager, match_manager, ranking_manager

LOGGER = get_logger("ui.cache")


def update_cache(force: bool = False):
    """Write/Rewrite to st.session_state data from database as dataframe"""
    # if ("df_players" not in st.session_state) or force or (st.session_state.df_players is None): # fmt: skip
    if ("df_players" not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state.df_players = player_manager.get_all_players(
                session=session, as_df=True
            )
        st.session_state.player_names = list(st.session_state.df_players["name"])
    if ("df_teams" not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state.df_teams = player_manager.get_all_teams(
                session=session, as_df=True
            )
    # if ("df_matches" not in st.session_state) or force or (st.session_state.df_matches is None): # fmt: skip
    if ("df_matches" not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state.df_matches = match_manager.get_all_matches(
                session=session, as_df=True
            )
    # if ("df_elo_hist" not in st.session_state) or force or (st.session_state.df_elo_hist is None): # fmt: skip
    if ("df_elo_hist" not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state.df_elo_hist = ranking_manager.get_elo_rating_history(
                session=session, as_df=True
            )


def refresh_cache():
    update_cache(force=True)
    LOGGER.info("refreshed cache")
