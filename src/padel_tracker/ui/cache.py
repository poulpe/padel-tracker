from enum import StrEnum
from concurrent.futures.thread import ThreadPoolExecutor

import streamlit as st

from padel_tracker.database.db import DB, Session
from padel_tracker.utils.logs import get_logger
from padel_tracker.services import (
    player_manager,
    match_manager,
    ranking_manager,
    league_manager,
)

LOGGER = get_logger("ui.cache")


class CacheKey(StrEnum):
    df_players = "df_players"
    df_teams = "df_teams"
    df_teams_all_leagues = "df_teams_all_leagues"
    df_matches = "df_matches"
    df_matches_all_leagues = "df_matches_all_leagues"
    df_elo_hist = "df_elo_hist"
    df_leagues = "df_leagues"
    df_linkplayerleague = "df_linkplayerleague"


ALL_CACHE_KEYS = tuple(CacheKey)

# TODO: big mucho : have df_players_all_leagues, df_teams_all_leagues, df_matches_all_leagues, df_leagues


def update_cache_leagues(session: Session, force: bool = False):
    key = str(CacheKey.df_leagues)
    if (key not in st.session_state) or force:
        st.session_state[key] = league_manager.get_all_leagues(
            session=session, as_df=True
        )
        try:
            st.session_state.league_names = list(st.session_state[key]["name"])
        except KeyError:
            st.session_state.league_names = None
            st.warning(
                st.session_state.translator("no_league_database_error"), icon="💢"
            )
            # st.stop()


def update_cache_players(session: Session, force: bool = False):
    key = str(CacheKey.df_players)
    if (key not in st.session_state) or force:
        st.session_state[key] = player_manager.get_all_players_from_league(
            session=session,
            as_df=True,
            league_name=st.session_state.league_name,
        )
        try:
            st.session_state.player_names = list(st.session_state[key]["name"])
        except KeyError:
            st.warning(
                st.session_state.translator("not_enough_players_database_error"),
                icon="💢",
            )
            # st.stop()


def update_cache_teams(session: Session, force: bool = False):
    key = str(CacheKey.df_teams)
    if (key not in st.session_state) or force:
        st.session_state[key] = player_manager.get_all_teams_from_league(
            session=session,
            as_df=True,
            league_name=st.session_state.league_name,
        )
    key = str(CacheKey.df_teams_all_leagues)
    if (key not in st.session_state) or force:
        st.session_state[key] = player_manager.get_all_teams(
            session=session,
            as_df=True,
        )


def update_cache_matches(session: Session, force: bool = False):
    key = str(CacheKey.df_matches)
    if (key not in st.session_state) or force:
        st.session_state[key] = match_manager.get_all_matches_from_league(
            session=session,
            as_df=True,
            league_name=st.session_state.league_name,
        )
    key = str(CacheKey.df_matches_all_leagues)
    if (key not in st.session_state) or force:
        st.session_state[key] = match_manager.get_all_matches(
            session=session,
            as_df=True,
        )


def update_cache_elo_hist(session: Session, force: bool = False):
    key = str(CacheKey.df_elo_hist)
    if (key not in st.session_state) or force:
        st.session_state[key] = (
            ranking_manager.get_all_elo_rating_histories_from_players_in_league(
                session=session,
                as_df=True,
                league_name=st.session_state.league_name,
            )
        )


def update_cache_linkplayerleague(session: Session, force: bool = False):
    key = str(CacheKey.df_linkplayerleague)
    if (key not in st.session_state) or force:
        st.session_state[key] = league_manager.get_linkplayerleague_from_league(
            session=session,
            league_name=st.session_state.league_name,
            as_df=True,
        )


# TODO : try threaded update_cache (i.e : this func becomes apply_update_cache and be called in "new_update_cache" below)
def update_cache(
    force: bool = False,
    only: str | CacheKey | tuple[str] | tuple[CacheKey] = ALL_CACHE_KEYS,
):
    """Write/Rewrite to st.session_state data from database as dataframe"""
    if isinstance(only, (str, CacheKey)):
        only = tuple([only])

    with DB.get_session() as session:
        if CacheKey.df_leagues in only:
            update_cache_leagues(session=session, force=force)

        if CacheKey.df_players in only:
            update_cache_players(session=session, force=force)

        if CacheKey.df_teams in only:
            update_cache_teams(session=session, force=force)

        if CacheKey.df_matches in only:
            update_cache_matches(session=session, force=force)

        if CacheKey.df_elo_hist in only:
            update_cache_elo_hist(session=session, force=force)

        if CacheKey.df_linkplayerleague in only:
            update_cache_linkplayerleague(session=session, force=force)


# def new_update_cache(
#     force: bool = False,
#     only: str | CacheKey | tuple[str] | tuple[CacheKey] = ALL_CACHE_KEYS,
#     thread_pool:ThreadPoolExecutor=None,
# ):
#     if thread_pool:
#         thread_pool.submit(apply_update_cache, force=force, only=only)
#     else:
#         apply_update_cache(force=force, only=only)


def refresh_cache(
    only: str | CacheKey | tuple[str] | tuple[CacheKey] = ALL_CACHE_KEYS,
    thread_pool: ThreadPoolExecutor = None,
):
    update_cache(force=True, only=only)  # thread_pool=thread_pool
    if isinstance(only, tuple):
        str_only = f"{[str(key) for key in only]}"
    else:
        str_only = str(only)
    LOGGER.info(f"refreshed cache for keys={str_only}")


def check_not_empty_database_matches() -> None:
    key = CacheKey.df_elo_hist
    if key in st.session_state:
        if len(st.session_state[key]) == 0:
            st.warning(
                st.session_state.translator("no_match_database_error"), icon="💢"
            )
            st.stop()


def check_not_empty_database_players() -> None:
    key = str(CacheKey.df_players)
    if key in st.session_state:
        if len(st.session_state[key]) < 4:
            st.warning(
                st.session_state.translator("not_enough_players_database_error"),
                icon="💢",
            )
            st.stop()
