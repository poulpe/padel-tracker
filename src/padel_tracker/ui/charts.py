from pathlib import Path

import streamlit as st
import pandas as pd
import altair as alt

# from padel_tracker.database.db import get_db_session
# from padel_tracker.services.ranking_manager import get_elo_rating_history
from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR

def make_overview_elo_history_chart(
    df_elo_history:pd.DataFrame=None,
    translator:LanguageTranslator=DEFAULT_TRANSLATOR,
) -> None:
    # if df_elo_history is None:
    #     # Get db_data as df
    #     with get_db_session() as session:
    #         df_elo_history = get_elo_rating_history(session, as_df=True).copy()
    ## Keep only useful columns
    col_to_keep = ["date", "elo_rating", "player_name", "elo_rating_gain"]
    df_elo_history = df_elo_history[col_to_keep]
    ## Rename to use user friendly/language names
    df_elo_history = df_elo_history.rename(columns=translator.dict_lang)

    # Create chart
    x_param = translator("date")
    y_param = translator("elo_rating")
    color_param = translator("player_name")
    #title = alt.Title("Billboard", fontSize=30, align="center", anchor="middle", subtitle=f"{y_param}", subtitleFontSize=20)
    chart = alt.Chart(df_elo_history).mark_line(point=True).encode(
        x=alt.X(x_param, type="temporal"),
        y=alt.Y(y_param, scale=alt.Scale(zero=False)),
        color=alt.Color(color_param),
        tooltip=[x_param,color_param,y_param,translator("elo_rating_gain")],
    ).interactive()

    # Plug it to Streamlit
    st.altair_chart(chart, use_container_width=True)

def make_DUMMY_overview_elo_history_chart():
    path_df = get_absolute_path(__file__,"./df_elo_history.csv")
    make_overview_elo_history_chart(pd.read_csv(path_df), translator=st.session_state.translator)