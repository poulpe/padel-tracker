import streamlit as st
import pandas as pd

from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import (
    get_all_players_from_league,
    get_all_teams_from_league,
)
from padel_tracker.services.league_manager import get_linkplayerleague_from_league
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR


# TODO : adapt make_player_overview_table to league
def make_player_overview_table(
    df_players: pd.DataFrame = None,
    df_linkplayerleague: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    extra_col: bool | list[str] = False,
    is_single: bool = False,
    use_container_width: bool = True,
    league_name: str = None,
) -> None:
    """
    Parameters
    ----------
    df_players
    df_linkplayerleague
    translator
    extra_col:bool|list[str]
        If True, will add default extra columns ["best_elo_rating", "best_rank", "creation_date"].
        If list[str], will use the ones provided.
    is_single
    use_container_width
    """
    # Get data as df in db if not provided
    if df_players is None:
        with DB.get_session() as session:
            df_players = get_all_players_from_league(
                session=session, league_name=league_name, as_df=True
            ).copy()
    else:
        df_players = df_players.copy()
    if df_linkplayerleague is None:
        with DB.get_session() as session:
            df_linkplayerleague = get_linkplayerleague_from_league(
                session=session, league_name=league_name, as_df=True
            ).copy()
    else:
        df_linkplayerleague = df_linkplayerleague.copy()
    # Join df_linkplayerleague to df_players (for rank and best_rank)
    df_linkplayerleague = df_linkplayerleague[["player_name", "rank", "best_rank"]]
    df_linkplayerleague = df_linkplayerleague.rename(columns={"player_name": "name"})
    df_players = pd.merge(df_players, df_linkplayerleague, on="name")
    # Deduct extras from current data
    df_players["ratio_vd"] = df_players["nb_victories"] / df_players["nb_defeats"]
    # Keep only useful columns
    col_to_keep = []
    if not is_single:
        col_to_keep += ["name"]
    col_to_keep += [
        "elo_rating",
        "rank",
        "nb_matches",
        "nb_victories",
        "nb_defeats",
        "ratio_vd",
        "last_match_date",
    ]
    if extra_col:
        if isinstance(extra_col, bool):
            col_to_keep += ["best_elo_rating", "best_rank", "creation_date"]
        else:
            col_to_keep += extra_col
    df_players = df_players[col_to_keep].copy()
    df_players = df_players.sort_values(by="rank")
    df_players = df_players.rename(columns=translator.dict_lang)
    column_config = {
        translator("last_match_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
        translator("creation_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
    }
    st.dataframe(
        df_players,
        hide_index=True,
        use_container_width=use_container_width,
        column_config=column_config,
    )


# TOCHECK : adapt make_team_overview_table to league
def make_team_overview_table(
    df_teams: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    extra_col: bool | list[str] = False,
    is_single: bool = False,
    use_container_width: bool = True,
    league_name: str = None,
) -> None:
    """
    Parameters
    ----------
    df_teams
    translator
    extra_col:bool|list[str]
        If True, will add default extra columns ["best_elo_rating", "best_rank", "creation_date"].
        If list[str], will use the ones provided.
    is_single
    use_container_width
    """
    # Get data as df in db if not provided
    if df_teams is None:
        with DB.get_session() as session:
            df_teams = get_all_teams_from_league(
                session=session, league_name=league_name, as_df=True
            ).copy()
    else:
        df_teams = df_teams.copy()
    # Deduct extras from current data
    df_teams["ratio_vd"] = df_teams["nb_victories"] / df_teams["nb_defeats"]
    # Keep only useful columns
    col_to_keep = []
    if not is_single:
        col_to_keep += ["name"]
    col_to_keep += [
        "elo_rating",
        # "rank",
        "nb_matches",
        "nb_victories",
        "nb_defeats",
        "ratio_vd",
        "last_match_date",
    ]
    if extra_col:
        if isinstance(extra_col, bool):
            col_to_keep += ["best_elo_rating"]
        else:
            col_to_keep += extra_col
    df_teams = df_teams[col_to_keep].copy()
    df_teams = df_teams.sort_values(by="elo_rating")
    df_teams = df_teams.rename(columns=translator.dict_lang)
    column_config = {
        translator("last_match_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
        translator("creation_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
    }
    st.dataframe(
        df_teams,
        hide_index=True,
        use_container_width=use_container_width,
        column_config=column_config,
    )
