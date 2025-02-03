import sys
from enum import StrEnum

import streamlit as st

from padel_tracker.database.db import DB
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
    df_matches = "df_matches"
    df_elo_hist = "df_elo_hist"
    df_leagues = "df_leagues"


ALL_CACHE_KEYS = tuple(CacheKey)


def update_cache_leagues(force: bool = False):
    key = str(CacheKey.df_leagues)
    if (key not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state[key] = league_manager.get_all_leagues(
                session=session, as_df=True
            )
        try:
            st.session_state.league_names = list(st.session_state[key]["name"])
        except KeyError:
            st.session_state.league_names = None
            st.error(st.session_state.translator("empty_database"), icon="💢")
            return


def update_cache_players(force: bool = False):
    key = str(CacheKey.df_players)
    if (key not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state[key] = player_manager.get_all_players_from_league(
                session=session,
                as_df=True,
                league_name=st.session_state.league_name,
            )
        try:
            st.session_state.player_names = list(st.session_state[key]["name"])
        except KeyError:
            st.error(st.session_state.translator("empty_database"), icon="💢")
            return


def update_cache_teams(force: bool = False):
    key = str(CacheKey.df_teams)
    if (key not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state[key] = player_manager.get_all_teams_from_league(
                session=session,
                as_df=True,
                league_name=st.session_state.league_name,
            )


def update_cache_matches(force: bool = False):
    key = str(CacheKey.df_matches)
    if (key not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state[key] = match_manager.get_all_matches_from_league(
                session=session,
                as_df=True,
                league_name=st.session_state.league_name,
            )


def update_cache_elo_hist(force: bool = False):
    key = str(CacheKey.df_elo_hist)
    if (key not in st.session_state) or force:
        with DB.get_session() as session:
            st.session_state[key] = (
                ranking_manager.get_all_elo_rating_histories_from_players_in_league(
                    session=session,
                    as_df=True,
                    league_name=st.session_state.league_name,
                )
            )


def update_cache(
    force: bool = False,
    only: str | CacheKey | tuple[str] | tuple[CacheKey] = ALL_CACHE_KEYS,
):
    """Write/Rewrite to st.session_state data from database as dataframe"""
    if isinstance(only, (str, CacheKey)):
        only = tuple([only])

    if CacheKey.df_leagues in only:
        update_cache_leagues(force=force)

    if CacheKey.df_players in only:
        update_cache_players(force=force)

    if CacheKey.df_teams in only:
        update_cache_teams(force=force)

    if CacheKey.df_matches in only:
        update_cache_matches(force=force)

    if CacheKey.df_elo_hist in only:
        update_cache_elo_hist(force=force)


def refresh_cache(only: str | CacheKey | tuple[str] | tuple[CacheKey] = ALL_CACHE_KEYS):
    update_cache(force=True, only=only)
    LOGGER.info("refreshed cache")


def check_not_empty_database_matches() -> None:
    key = CacheKey.df_elo_hist
    if key in st.session_state:
        if len(st.session_state[key]) == 0:
            st.warning(st.session_state.translator("empty_database_error"), icon="💢")
            sys.exit()


def check_not_empty_database_players() -> None:
    key = str(CacheKey.df_players)
    if key in st.session_state:
        if len(st.session_state[key]) < 4:
            st.warning(
                st.session_state.translator("not_enough_players_database_error"),
                icon="💢",
            )
            sys.exit()
