import streamlit as st
import pandas as pd
import altair as alt

from padel_tracker.database.db import DB
from padel_tracker.services.ranking_manager import get_elo_rating_history
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR


def make_overview_elo_history_chart(
    df_elo_history: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    font_size_header: int = 30,
    font_size_subheader: int = 20,
) -> None:
    # Write header
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div style="font-size: {font_size_header}px; font-weight: bold; margin: 0;"> Billboard </div>
            <div style="font-size: {font_size_subheader}px; margin: 0;"> {translator("ranking_evolution")} </div>
            <br>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch data
    if df_elo_history is None:
        # Get db_data as df
        with DB.get_session() as session:
            df_elo_history = get_elo_rating_history(session, as_df=True).copy()
    ## Keep only useful columns
    col_to_keep = ["date", "elo_rating", "player_name", "elo_rating_gain"]
    df_elo_history = df_elo_history[col_to_keep]
    ## Rename to use user friendly/language names
    df_elo_history = df_elo_history.rename(columns=translator.dict_lang)

    # Create chart
    x_param = translator("date")
    y_param = translator("elo_rating")
    color_param = translator("player_name")
    chart = (
        alt.Chart(df_elo_history)
        .mark_line(point=True)
        .encode(
            x=alt.X(x_param, type="temporal"),
            y=alt.Y(y_param, scale=alt.Scale(zero=False)),
            color=alt.Color(color_param),
            tooltip=[x_param, color_param, y_param, translator("elo_rating_gain")],
        )
        .interactive()
    )

    # Plug it to Streamlit
    st.altair_chart(chart, use_container_width=True)
