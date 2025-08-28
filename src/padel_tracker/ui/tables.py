import streamlit as st
import pandas as pd

from padel_tracker.utils.paths import sanitize_filename
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR


@st.cache_data(max_entries=32)
def _generate_player_overview_table(
    df_players: pd.DataFrame,
    df_linkplayerleague: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    extra_col: bool | list[str] = False,
    is_single: bool = False,
) -> pd.DataFrame:
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
    df_players = df_players.copy()
    # Deduct extras from current data
    df_players["rank"] = (
        df_players["elo_rating"].rank(ascending=False, method="min").astype(int)
    )
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
        if df_linkplayerleague is None:
            err_msg = "'extra_col' specified without 'df_linkplayerleague', cannot deduct best_rank"
            raise ValueError(err_msg)
        # Join df_linkplayerleague to df_players (for best_rank only)
        df_link = df_linkplayerleague.copy()
        df_link = df_link[["player_name", "best_rank"]]
        df_link = df_link.rename(columns={"player_name": "name"})
        df_players = pd.merge(df_players, df_link, on="name")
        if isinstance(extra_col, bool):
            col_to_keep += ["best_elo_rating", "best_rank", "creation_date"]
        else:
            col_to_keep += extra_col
    df_players = df_players[col_to_keep].copy()
    df_players = df_players.sort_values(by="rank")
    df_players = df_players.rename(columns=translator.dict_lang)
    return df_players


def apply_highlight_player_row(
    row, player_name: str = "", translator: LanguageTranslator = DEFAULT_TRANSLATOR
):
    return [
        (
            "background-color: rgba(255, 70, 0, 0.05)"
            if row[translator("name")] == player_name
            else ""
        )
        for _ in row
    ]


def make_player_overview_table(
    df_players: pd.DataFrame,
    df_linkplayerleague: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    extra_col: bool | list[str] = False,
    is_single: bool = False,
    use_container_width: bool = True,
    highlight_player_name: str = None,
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
    df_players = _generate_player_overview_table(
        df_players=df_players,
        df_linkplayerleague=df_linkplayerleague,
        translator=translator,
        extra_col=extra_col,
        is_single=is_single,
    )
    column_config = {
        translator("last_match_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
        translator("creation_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
        translator("ratio_vd"): st.column_config.NumberColumn(format="%.3f"),
        translator("rank"): st.column_config.NumberColumn(format="%i"),
        translator("best_rank"): st.column_config.NumberColumn(format="%i"),
    }
    if highlight_player_name:
        df_plot = df_players.style.apply(
            apply_highlight_player_row,
            player_name=highlight_player_name,
            translator=translator,
            axis=1,
        )
    else:
        df_plot = df_players
    st.dataframe(
        df_plot,
        hide_index=True,
        use_container_width=use_container_width,
        column_config=column_config,
    )


@st.cache_data(max_entries=32)
def _generate_team_overview_table(
    df_teams: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    extra_col: bool | list[str] = False,
    is_single: bool = False,
) -> pd.DataFrame:
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
    df_teams = df_teams.copy()
    # Deduct extras from current data
    df_teams["ratio_vd"] = df_teams["nb_victories"] / df_teams["nb_defeats"]
    # Keep only useful columns
    col_to_keep = []
    if not is_single:
        col_to_keep += ["name"]
    col_to_keep += [
        "elo_rating",
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
    return df_teams


def make_team_overview_table(
    df_teams: pd.DataFrame,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    extra_col: bool | list[str] = False,
    is_single: bool = False,
    use_container_width: bool = True,
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
    df_teams = _generate_team_overview_table(
        df_teams=df_teams,
        translator=translator,
        extra_col=extra_col,
        is_single=is_single,
    )
    column_config = {
        translator("last_match_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
        translator("creation_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
        translator("ratio_vd"): st.column_config.NumberColumn(format="%.3f"),
    }
    st.dataframe(
        df_teams,
        hide_index=True,
        use_container_width=use_container_width,
        column_config=column_config,
    )


def make_league_overview_table(
    df_league: pd.DataFrame,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    is_single: bool = False,
    use_container_width: bool = True,
) -> None:
    col_to_keep = []
    if not is_single:
        col_to_keep += ["name"]
    col_to_keep += ["nb_players", "nb_matches", "last_match_date", "creation_date"]
    df_plot = df_league[col_to_keep].copy()
    df_plot = df_plot.rename(columns=translator.dict_lang)
    column_config = {
        translator("last_match_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
        translator("creation_date"): st.column_config.DateColumn(format="DD-MM-YYYY"),
    }
    st.dataframe(
        df_plot,
        hide_index=True,
        use_container_width=use_container_width,
        column_config=column_config,
    )


# Download functions
@st.cache_data
def convert_df_for_csv_download(df: pd.DataFrame):
    # Drop id columns
    col_to_delete = []
    for col in df.columns:
        if col == "id" or "_id" in col:
            col_to_delete.append(col)
    df = df.drop(columns=col_to_delete)
    return df.to_csv(index=False)


def make_download_as_csv_button(
    df: pd.DataFrame,
    file_name: str,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    label: str | None = None,
) -> None:
    if label is None:
        label = translator("download_as_csv")
    st.download_button(
        label=label,
        data=convert_df_for_csv_download(df),
        file_name=sanitize_filename(file_name),
        mime="text/csv",
        icon=":material/download:",
        width="stretch",
    )
