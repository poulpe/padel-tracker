import streamlit as st
import pandas as pd
import altair as alt

from padel_tracker.database.db import DB
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR
from padel_tracker.services import player_manager, ranking_manager


# TODO : selectable metric
def make_overview_elo_history_chart(
    df_elo_hist: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
) -> None:
    # Fetch data
    if df_elo_hist is None:
        # Get db_data as df (and manage limit (4 players per match...))
        limit_last_histories = limit_last_matches * 4 if limit_last_matches else None
        with DB.get_session() as session:
            df_elo_hist = ranking_manager.get_elo_rating_history(
                session, as_df=True, limit_last=limit_last_histories
            ).copy()
    else:
        df_elo_hist = df_elo_hist.copy()
        if limit_last_matches:
            df_elo_hist = df_elo_hist.tail(limit_last_matches * 4)
    ## Keep only useful columns
    col_to_keep = ["date", "elo_rating", "player_name", "elo_rating_gain", "match_name"]
    df_elo_hist = df_elo_hist[col_to_keep]
    ## Rename to use user friendly/language names
    df_elo_hist = df_elo_hist.rename(columns=translator.dict_lang)

    # Create chart
    x_param = translator("date")
    y_param = translator("elo_rating")
    color_param = translator("player_name")
    chart = (
        alt.Chart(df_elo_hist)
        .mark_line(point=True)
        .encode(
            x=alt.X(x_param, type="temporal"),
            y=alt.Y(y_param, scale=alt.Scale(zero=False)),
            color=alt.Color(color_param),
            tooltip=[
                x_param,
                color_param,
                y_param,
                translator("elo_rating_gain"),
                translator("match_name"),
            ],
        )
        .interactive()
    )

    # Plug it to Streamlit
    st.altair_chart(chart, use_container_width=True)


# TODO : plug player history chart
def make_player_metric_history_chart(
    player_name: str,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
) -> None:
    metric = st.pills(
        label=translator("metric"),
        options=[translator("elo_rating"), translator("nb_won_games_diff")],
        default=translator("nb_won_games_diff"),
    )
    if metric is None:
        metric = translator("nb_won_games_diff")
    # Fetch data vs
    col_to_keep = [
        translator("date"),
        metric,
        translator("result"),
        translator("match_name"),
    ]
    with DB.get_session() as session:
        player = player_manager.get_player_from_name(session, name=player_name)
        list_data = []
        if metric == translator("elo_rating"):
            for elo_rating_history in player.elo_rating_history:
                row = {
                    translator("date"): elo_rating_history.date,
                    translator("elo_rating"): elo_rating_history.elo_rating,
                    translator("elo_rating_gain"): elo_rating_history.elo_rating_gain,
                    translator("match_name"): elo_rating_history.match_name,
                }
                if elo_rating_history.elo_rating_gain > 0:
                    match_result = translator("victory")
                else:
                    match_result = translator("defeat")
                row[translator("result")] = match_result
                list_data.append(row)
            col_to_keep += [translator("elo_rating_gain")]
            extra_tooltip = [translator("elo_rating_gain")]
        elif metric == translator("nb_won_games_diff"):
            for match in player.matches:
                row = {
                    translator("date"): match.date,
                    translator("nb_won_games_diff"): match.nb_won_games_diff,
                    translator("score"): match.score,
                    translator("match_name"): match.name,
                }
                if player in match.teams[0].players:
                    player_won = match.team1_won
                else:
                    player_won = not match.team1_won
                row[translator("result")] = (
                    translator("victory") if player_won else translator("defeat")
                )
                list_data.append(row)
            col_to_keep += [translator("score")]
            extra_tooltip = [translator("score"), translator("result")]
        else:
            raise ValueError(f"{metric=} not supported")

    ## Keep only useful columns
    df_hist = pd.DataFrame(list_data)
    df_hist[translator("date")] = pd.to_datetime(df_hist[translator("date")])
    df_hist = df_hist[col_to_keep]
    ## Rename to use user friendly/language names
    df_hist = df_hist.rename(columns=translator.dict_lang)

    # Create chart
    x_param = translator("date")
    y_param = metric
    color_param = translator("result")
    tooltip = [x_param, y_param, f"{color_param}:N", translator("match_name")]
    if metric == translator("elo_rating"):
        base_chart = alt.Chart(df_hist).mark_rule(size=50)
    elif metric == translator("nb_won_games_diff"):
        base_chart = alt.Chart(df_hist).mark_bar()
    chart = base_chart.encode(
        x=alt.X(
            x_param,
            type="ordinal",
            timeUnit="yearmonthdatehours",
            title=translator("date"),
        ),
        y=alt.Y(y_param, scale=alt.Scale(zero=False)),
        color=alt.Color(
            color_param,
            type="nominal",
            scale=alt.Scale(
                domain=[translator("victory"), translator("defeat")], scheme="tableau10"
            ),
        ),
        # shape=alt.Shape(color_param),
        tooltip=list(set(tooltip + extra_tooltip)),
    ).interactive()

    # Plug it to Streamlit
    st.altair_chart(chart, use_container_width=True)


def make_player_metric_history_chart_form(
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
) -> None:
    # Write header
    write_header("Analytics", translator("evolution"))

    with DB.get_session() as session:
        list_players = player_manager.get_all_players(session=session)
        player_names = [p.name for p in list_players]

    player_name = st.selectbox(
        label=translator("player_name"),
        options=player_names,
        placeholder=translator("player"),
    )

    make_player_metric_history_chart(player_name=player_name, translator=translator)
