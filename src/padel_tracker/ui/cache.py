from enum import StrEnum

import pandas as pd
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from padel_tracker.utils.errors import UserNotFoundError
from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.conf import is_test_mode
from padel_tracker.database.db import DB, Session
from padel_tracker.models.users import UserRole
from padel_tracker.services import (
    player_manager,
    match_manager,
    ranking_manager,
    league_manager,
    user_manager,
    event_manager,
)
from padel_tracker.ui.common import determine_is_logged_in
from padel_tracker.main import init_app

LOGGER = get_logger("ui.cache")


@st.cache_resource
def init_streamlit_app() -> None:
    """
    Init app and will run only once thanks to the @st.cache_resource
    (and not at every rerun or other session_state)
    """
    init_app()


class CacheKey(StrEnum):
    user = "user"
    df_leagues = "df_leagues"
    league_names = "league_names"
    league_admins = "league_admins"
    df_players = "df_players"
    # df_players_all_leagues = "df_players_all_leagues" # Optional
    player_names = "player_names"
    # player_names_all_leagues = "player_names_all_leagues" # Optional
    df_teams = "df_teams"
    df_teams_all_leagues = "df_teams_all_leagues"  # Optional
    df_matches = "df_matches"
    df_matches_all_leagues = "df_matches_all_leagues"
    df_elo_hist = "df_elo_hist"
    df_linkplayerleague = "df_linkplayerleague"
    df_events = "df_events"
    # df_rank_hist = "df_rank_hist"


ALL_CACHE_KEYS = tuple(CacheKey)
list_cache_keys_no_user = list(CacheKey)
list_cache_keys_no_user.remove(CacheKey.user)
CACHE_KEYS_NO_USER = tuple(list_cache_keys_no_user)


def update_cache_user(session: Session, force: bool = False):
    """
    Notes
    -----
    Don't do anything if in test mode, to allow defining user in tests files
    """
    key = str(CacheKey.user)
    if (key not in st.session_state) or force:
        if determine_is_logged_in():
            if not is_test_mode():
                auth_user_id = st.user["sub"]
                try:
                    user = user_manager.get_user_from_auth_user_id(
                        session=session, auth_user_id=auth_user_id
                    )
                    st.session_state.user = user.model_dump()
                    st.session_state.user["admin_leagues"] = [
                        league.name for league in user.admin_leagues
                    ]
                except UserNotFoundError:
                    # Means new user, will be redirected to "finalize_signup"
                    st.session_state.user = None
        else:
            st.session_state.user = None


def update_cache_leagues(session: Session, force: bool = False):
    key = str(CacheKey.df_leagues)
    if (key not in st.session_state) or force:
        # Get all public leagues
        df_leagues = league_manager.get_all_public_leagues(session=session, as_df=True)
        # Get current user leagues
        ## Fetch current user
        if "user" in st.session_state and st.session_state["user"]:
            # Case admin : all leagues
            user = st.session_state.user
            if "role" in user.keys() and user["role"] == UserRole.ADMIN:
                df_leagues_private = league_manager.get_all_private_leagues(
                    session=session, as_df=True
                )
                if not df_leagues_private.empty:
                    df_leagues = pd.concat(
                        [
                            df_leagues.dropna(axis=1, how="all"),
                            df_leagues_private.dropna(axis=1, how="all"),
                        ]
                    ).reset_index(drop=True)
            else:
                player_name = user["name"]
                if player_name:
                    df_leagues_user = league_manager.get_all_leagues_from_player(
                        session=session,
                        player_name=player_name,
                        as_df=True,
                    )
                    if not df_leagues_user.empty:
                        df_leagues = pd.concat(
                            [
                                df_leagues.dropna(axis=1, how="all"),
                                df_leagues_user.dropna(axis=1, how="all"),
                            ]
                        ).reset_index(drop=True)
        df_leagues = df_leagues.drop_duplicates(subset=["id"])
        st.session_state[key] = df_leagues
        try:
            st.session_state.league_names = list(df_leagues["name"])
        except KeyError:
            st.session_state.league_names = None
            # st.warning(
            #     st.session_state.translator("no_league_database_error"), icon="💢"
            # )


def update_cache_players(session: Session, force: bool = False):
    # Players from current league
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
            st.session_state.player_names = None
            # st.warning(
            #     st.session_state.translator("not_enough_players_database_error"),
            #     icon="💢",
            # )
    # # All players
    # key = str(CacheKey.player_names_all_leagues)
    # if (key not in st.session_state) or force:
    #     st.session_state[key] = player_manager.get_all_players_names(
    #         session=session,
    #     )


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


def update_cache_league_admins(session: Session, force: bool = False):
    key = str(CacheKey.league_admins)
    if (key not in st.session_state) or force:
        st.session_state[key] = league_manager.get_admin_names_from_league_name(
            session=session,
            name=st.session_state.league_name,
        )


def update_cache_events(session: Session, force: bool = False):
    key = str(CacheKey.df_events)
    if (key not in st.session_state) or force:
        st.session_state[key] = event_manager.get_all_events_from_league(
            session=session,
            league_name=st.session_state.league_name,
            as_df=True,
        )


DICT_UPDATE_FUNC_VS_KEY = {
    CacheKey.user: update_cache_user,
    CacheKey.df_leagues: update_cache_leagues,
    CacheKey.league_names: update_cache_leagues,
    CacheKey.df_players: update_cache_players,
    CacheKey.player_names: update_cache_players,
    CacheKey.df_teams: update_cache_teams,
    CacheKey.df_teams_all_leagues: update_cache_teams,
    CacheKey.df_matches: update_cache_matches,
    CacheKey.df_matches_all_leagues: update_cache_matches,
    CacheKey.df_elo_hist: update_cache_elo_hist,
    CacheKey.df_linkplayerleague: update_cache_linkplayerleague,
    CacheKey.league_admins: update_cache_league_admins,
    CacheKey.df_events: update_cache_events,
    # CacheKey.df_rank_hist: update_cache_rank_hist,
    # CacheKey.df_players_all_leagues:update_cache_players,
    # CacheKey.player_names_all_leagues:update_cache_players,
}


def apply_update_cache_standard(
    force: bool = False,
    only: str | CacheKey | tuple[str] | tuple[CacheKey] = ALL_CACHE_KEYS,
):
    """Write/Rewrite to st.session_state data from database as dataframe"""
    if isinstance(only, (str, CacheKey)):
        only = tuple([only])

    with DB.get_session() as session:
        for key in only:
            update_func = DICT_UPDATE_FUNC_VS_KEY[key]
            update_func(session=session, force=force)


# THREADED TRIALS
# Issues with threaded and writing to st.session_state
# TODO (prio 3) : try threaded update_cache (i.e : this func becomes apply_update_cache and be called in "new_update_cache" below)


def update_cache(
    force: bool = False,
    only: str | CacheKey | tuple[str] | tuple[CacheKey] = ALL_CACHE_KEYS,
    threaded: bool = False,
):
    if threaded:
        # get_thread_pool().submit(apply_update_cache_standard, force=force, only=only)
        apply_update_cache_standard(force=force, only=only)  # _threaded
    else:
        apply_update_cache_standard(force=force, only=only)


def refresh_cache(
    only: str | CacheKey | tuple[str] | tuple[CacheKey] = CACHE_KEYS_NO_USER,
    threaded: bool = False,
):
    update_cache(force=True, only=only, threaded=threaded)
    if isinstance(only, tuple):
        str_only = f"{[str(key) for key in only]}"
    else:
        str_only = str(only)
    LOGGER.info(f"refreshed cache for keys={str_only}")


### Checks ###


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
            # TODO 3) : display button to go to "Add player in league" form (page_add_player_in_league.py)
            st.stop()


def check_not_empty_database_leagues() -> None:
    key = str(CacheKey.df_leagues)
    if key in st.session_state:
        if len(st.session_state[key]) == 0:
            st.warning(
                st.session_state.translator("no_league_database_error"),
                icon="💢",
            )
            st.stop()


def determine_session_state_device_type() -> None:
    if ("screen_inner_width" not in st.session_state) or (
        st.session_state.screen_inner_width is None
    ):
        screen_inner_width = streamlit_js_eval(
            js_expressions="window.innerWidth", key="WIDTH", want_output=True
        )
        device_type = "pc"  # Default
        if screen_inner_width is not None:
            device_type = "mobile" if screen_inner_width < 550 else "pc"
            st.session_state.screen_inner_width = screen_inner_width
        st.session_state.device_type = device_type


def determine_session_state_league_name() -> None:
    if "league_name" not in st.session_state:
        # Try fetching default league from user
        user_league = None
        if ("user" in st.session_state) and (st.session_state.user):
            user_league = st.session_state.user["default_league_name"]
        # Determine default league
        if user_league:
            st.session_state.league_name = user_league
        else:
            try:
                st.session_state.league_name = st.session_state.league_names[0]
            except (KeyError, TypeError):
                # st.warning(translator("no_league_database_error"), icon="💢")
                # TODO (prio3): fallback display page_add_league (because pg.run() won't run)
                st.stop()
    elif (
        "forced_league_name" in st.session_state and st.session_state.forced_league_name
    ):
        st.session_state.league_name = st.session_state.forced_league_name
        st.session_state.forced_league_name = None
        refresh_cache()  # Already all cache keys no user by default


def force_league_name_refresh(league_name: str) -> None:
    """Set `forced_league_name` in session state to force league_name update at next script run/rerun.
    Must do that because cannot assign value directly of already instantiated st.selectbox of 'league_name'.
    """
    st.session_state.forced_league_name = league_name


### Optional cache (on-demand)
def update_cache_rank_hist_current_league(session: Session, force: bool = False):
    """To update only on demand, not mandatory to refresh each time to save some db calls"""
    key = "df_rank_hist"
    if (key not in st.session_state) or force:
        st.session_state[key] = ranking_manager.get_all_rank_histories_from_league(
            session=session,
            as_df=True,
            league_name=st.session_state.league_name,
        )
