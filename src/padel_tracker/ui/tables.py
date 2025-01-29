import streamlit as st
import pandas as pd

from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import get_all_players
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR


def make_player_overview_table(
    df_players: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
) -> None:
    # Get data as df in db if not provided
    if df_players is None:
        with DB.get_session() as session:
            df_players = get_all_players(session=session, as_df=True).copy()
    # Keep only useful columns
    col_to_keep = [
        "name",
        "elo_rating",
        "rank",
        "nb_matches",
        "nb_victories",
        "nb_defeats",
        "last_match_date",
    ]
    # optional_col = ["last_match_date", "best_elo_rating", "best_rank", "creation_date", "elo_k"]
    df_players = df_players[col_to_keep].copy()
    df_players = df_players.sort_values(by="rank")
    df_players = df_players.rename(columns=translator.dict_lang)
    column_config = {
        translator.dict_lang["last_match_date"]: st.column_config.DateColumn(
            format="DD-MM-YYYY"
        ),
    }
    st.dataframe(
        df_players,
        hide_index=True,
        use_container_width=True,
        column_config=column_config,
    )
