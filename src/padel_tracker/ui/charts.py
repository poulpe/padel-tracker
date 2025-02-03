import streamlit as st
import pandas as pd
import altair as alt

from padel_tracker.database.db import DB
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR
from padel_tracker.services import ranking_manager


def make_overview_elo_history_chart(
    df_elo_hist: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
    league_name: str = None,
) -> None:
    # Fetch data if not given
    if df_elo_hist is None:
        # Resolve league
        if not league_name:
            league_name = st.session_state.league_name
        # Get db_data as df (and manage limit (4 players per match...))
        limit_last_histories = limit_last_matches * 4 if limit_last_matches else None
        with DB.get_session() as session:
            df_elo_hist = (
                ranking_manager.get_all_elo_rating_histories_from_players_in_league(
                    session,
                    league_name=league_name,
                    as_df=True,
                    limit_last=limit_last_histories,
                ).copy()
            )
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


def make_player_metric_history_chart(
    player_name: str,
    df_elo_hist: pd.DataFrame = None,
    df_matches: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
) -> None:
    # Metric selection
    metric = st.pills(
        label=translator("metric"),
        options=[translator("elo_rating"), translator("nb_won_games_diff")],
        default=translator("nb_won_games_diff"),
    )
    if metric is None:
        metric = translator("nb_won_games_diff")

    # Fetch data
    col_to_keep = ["date", "match_name", "result"]
    extra_tooltip = []
    if metric == translator("elo_rating"):
        # Fetch data if not given
        if df_elo_hist is None:
            # Get db_data as df
            with DB.get_session() as session:
                df_hist = ranking_manager.get_player_elo_rating_histories(
                    session=session,
                    player_name=player_name,
                    as_df=True,
                    limit_last=limit_last_matches,
                )
        else:
            df_hist = df_elo_hist.query(f"player_name == '{player_name}'").copy()
            if limit_last_matches:
                df_hist = df_hist.tail(limit_last_matches)
        ## Determine result
        df_hist["result"] = df_hist["elo_rating_gain"].apply(
            lambda x: translator("victory") if x > 0 else translator("defeat")
        )
        ## Keep only useful columns
        col_to_keep += ["elo_rating", "elo_rating_gain"]
        extra_tooltip += [translator("elo_rating_gain")]
    elif metric == translator("nb_won_games_diff"):
        # Fetch data if not given
        if df_matches is None:
            # TODO (prio 4): fetch df_matches from db...
            raise NotImplementedError()
            # Get db_data as df
            # with DB.get_session() as session:
            #     read_from_db(Pla)
            # player = player_manager.get_player_from_name(
            #     session=session, name=player_name
            # )
            # if limit_last_matches:
            #     player.matches
        else:
            df_hist = df_matches[df_matches["name"].str.contains(player_name)].copy()
            if limit_last_matches:
                df_hist = df_hist.tail(limit_last_matches)

        ## Determine result
        def apply_determine_result(row, player_name):
            team1, team2 = row["name"].replace(" vs ", "|").split("|")
            team1_players = set(team1.split("/"))
            team2_players = set(team2.split("/"))
            if player_name in team1_players:
                if row["team1_won"]:
                    row["result"] = translator("victory")
                else:
                    row["result"] = translator("defeat")
            elif player_name in team2_players:
                if row["team1_won"]:
                    row["result"] = translator("defeat")
                else:
                    row["result"] = translator("victory")
            return row

        df_hist = df_hist.apply(apply_determine_result, player_name=player_name, axis=1)
        ## Keep only useful
        df_hist = df_hist.rename(columns={"name": "match_name"})
        col_to_keep += ["nb_won_games_diff", "score"]
        extra_tooltip += [translator("score")]
    else:
        raise NotImplementedError(f"{metric=} not supported")

    ## Keep only useful columns
    df_hist = df_hist[col_to_keep]
    df_hist["date"] = pd.to_datetime(df_hist["date"])
    ## Rename to use user friendly/language names
    df_hist = df_hist.rename(columns=translator.dict_lang)

    # Create chart
    x_param = translator("date")
    y_param = metric
    color_param = translator("result")
    tooltip = [x_param, y_param, f"{color_param}:N", translator("match_name")]
    if metric == translator("elo_rating"):
        # TODO: better elo_rating (ensure no zero + maybe via points ?)
        base_chart = alt.Chart(df_hist).mark_bar()  # mark_rule(size=50)
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
