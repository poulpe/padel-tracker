import streamlit as st
import pandas as pd
import altair as alt

from padel_tracker.database.db import DB
from padel_tracker.models.events import EventCategory
from padel_tracker.services import ranking_manager
from padel_tracker.ui.cache import update_cache_rank_hist_current_league
from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_TRANSLATOR


@st.cache_data(max_entries=32)
def _generate_events_chart(
    df_events: pd.DataFrame, translator: LanguageTranslator = DEFAULT_TRANSLATOR
) -> alt.Chart:
    """As vertical lines, with color determined from event category + name label"""
    # Clean df
    ## Keep only useful columns
    col_to_keep = ["name", "date", "category", "description", "end_date"]
    df_events = df_events[col_to_keep].copy()
    df_events["date"] = pd.to_datetime(df_events["date"], errors="coerce")
    df_events["end_date"] = pd.to_datetime(df_events["end_date"], errors="coerce")
    ## Rename to use user friendly/language names
    dict_translated_categ = {cat.value: translator(cat.value) for cat in EventCategory}
    df_events["category"] = df_events["category"].replace(dict_translated_categ)
    df_events = df_events.rename(columns=translator.dict_lang)

    # Declare charts
    date_param = translator("date")
    name_param = translator("name")
    categ_param = translator("category")
    base_chart = alt.Chart(df_events).mark_rule(strokeWidth=2)
    chart_rules = base_chart.encode(
        x=alt.X(date_param + ":T", timeUnit="yearmonthdatehoursminutes"),
        color=alt.Color(categ_param + ":N", legend=None).scale(scheme="pastel1"),
        tooltip=[name_param, categ_param, date_param, translator("description")],
    )
    chart_labels = chart_rules.mark_text(
        align="right", baseline="top", dx=-5, dy=120  # dy=125 also OK
    ).encode(text=name_param + ":N", color=alt.Color(categ_param + ":N", legend=None))
    chart = chart_rules + chart_labels
    return chart


def add_events_to_chart(
    chart: alt.Chart,
    df_events: pd.DataFrame,
    df_main: pd.DataFrame = None,
    limit_last_matches: int = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
) -> alt.Chart:
    """
    Add event_rules chart to a time chart if df_events has events.
    If None, will just return chart as is

    Parameters
    ----------
    df_main:pd.DataFrame
        The main dataframe of the chart (i.e: df_elo_hist, df_matches...)
    """
    if (df_events is not None) and (not df_events.empty):
        # Fetch last df_main date, don't plot event prior last match
        if limit_last_matches:
            df_main = df_main.tail(limit_last_matches * 4)
            oldest_date = df_main["date"].min()
            df_events = df_events[df_events["date"] >= oldest_date]
        if not df_events.empty:
            chart += _generate_events_chart(df_events=df_events, translator=translator)
            chart = chart.resolve_scale(color="independent")
    return chart


@st.cache_data(max_entries=32)
def _generate_overview_elo_history_chart(
    df_elo_hist: pd.DataFrame,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
    temporal_time_scale: bool = True,
) -> alt.Chart:
    # Clean df
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
    elo_gain_param = translator("elo_rating_gain")
    player_selection = alt.selection_point(
        fields=[color_param], bind="legend", toggle="event"
    )
    if temporal_time_scale:
        # Keep only the "final result" of the day on 'df_elo_hist'
        df_elo_hist[x_param] = df_elo_hist[x_param].dt.date
        df_grouped = df_elo_hist.groupby(by=[x_param, color_param])
        df_elo_gain_sum = df_grouped[elo_gain_param].sum().reset_index()
        df_elo_hist_last = df_grouped.tail(1)
        df_elo_hist_last = pd.merge(
            df_elo_hist_last,
            df_elo_gain_sum,
            on=[x_param, color_param],
            suffixes=("_delete", ""),
        )
        df_elo_hist_last = df_elo_hist_last.drop(columns=[f"{elo_gain_param}_delete"])
        # Gen chart
        base_chart = alt.Chart(df_elo_hist_last).mark_line(point=True)
        chart = base_chart.encode(
            x=alt.X(x_param + ":T", title=x_param, timeUnit="yearmonthdate"),
            y=alt.Y(y_param, scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
            color=alt.Color(
                color_param, legend=alt.Legend(rowPadding=-50, labelPadding=0),
            ),
            opacity=alt.condition(player_selection, alt.value(1), alt.value(0.1)),
            tooltip=[x_param, color_param, y_param, elo_gain_param],
        )
    else:
        base_chart = alt.Chart(df_elo_hist).mark_line(point=True)
        chart = base_chart.encode(
            x=alt.X(
                f"{x_param}:O", title=x_param, timeUnit="yearmonthdatehoursminutes"
            ),
            y=alt.Y(y_param, scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
            color=alt.Color(
                color_param, legend=alt.Legend(rowPadding=-50, labelPadding=0),
            ),
            opacity=alt.condition(player_selection, alt.value(1), alt.value(0.1)),
            tooltip=[
                x_param,
                color_param,
                y_param,
                translator("elo_rating_gain"),
                translator("match_name"),
            ],
        )
    chart = chart.add_params(player_selection).interactive(bind_y=False)
    return chart


def make_overview_elo_history_chart(
    df_elo_hist: pd.DataFrame = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
    df_events: pd.DataFrame = None,
) -> None:
    # Button time scale
    _, right_col = st.columns([3.3, 1])
    temporal_time_scale = right_col.toggle(
        translator("time_scale"), help=translator("time_scale_help_message")
    )
    # Make chart
    chart = _generate_overview_elo_history_chart(
        df_elo_hist=df_elo_hist,
        translator=translator,
        limit_last_matches=limit_last_matches,
        temporal_time_scale=temporal_time_scale,
    )
    chart = add_events_to_chart(
        chart=chart,
        df_events=df_events,
        df_main=df_elo_hist,
        limit_last_matches=limit_last_matches,
        translator=translator,
    )
    # Plug it to Streamlit
    st.altair_chart(chart, width="stretch")


def _apply_determine_match_result(
    row: pd.Series, player_name: str, translator: LanguageTranslator
) -> pd.Series:
    """To apply on df_matches for a player"""
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


def _apply_determine_team_match_result(
    row: pd.Series, team_name: str, translator: LanguageTranslator
) -> pd.Series:
    """To apply on df_matches for a player"""
    team1, team2 = row["name"].replace(" vs ", "|").split("|")
    if team_name == team1:
        if row["team1_won"]:
            row["result"] = translator("victory")
        else:
            row["result"] = translator("defeat")
    elif team_name == team2:
        if row["team1_won"]:
            row["result"] = translator("defeat")
        else:
            row["result"] = translator("victory")
    return row


@st.cache_data(max_entries=32)
def _generate_player_metric_history_chart(
    player_name: str,
    df_matches: pd.DataFrame,
    df_elo_hist: pd.DataFrame,
    metric: str = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
    temporal_time_scale: bool = False,
) -> alt.Chart:
    # Metric selection
    if metric is None:
        metric = translator("nb_won_games_diff")

    # Fetch data
    col_to_keep = ["date", "match_name", "result"]
    extra_tooltip = []
    if metric == translator("elo_rating"):
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
        df_hist = df_matches[df_matches["name"].str.contains(player_name)].copy()
        if limit_last_matches:
            df_hist = df_hist.tail(limit_last_matches)
        ## Determine result
        df_hist = df_hist.apply(
            _apply_determine_match_result,
            player_name=player_name,
            translator=translator,
            axis=1,
        )
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
        base_chart = alt.Chart(df_hist).mark_bar()
        y_domain = (df_hist[y_param].min() * 0.95, df_hist[y_param].max() * 1.05)
    elif metric == translator("nb_won_games_diff"):
        base_chart = alt.Chart(df_hist).mark_bar()
        y_domain = (0, df_hist[y_param].max() * 1.2)
    x_type = "temporal" if temporal_time_scale else "ordinal"
    chart = base_chart.encode(
        x=alt.X(
            x_param,
            type=x_type,
            timeUnit="yearmonthdatehoursminutes",
            title=translator("date"),
        ),
        y=alt.Y(y_param, scale=alt.Scale(domain=y_domain)),
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
    return chart


@st.cache_data(max_entries=32)
def _generate_player_rank_history_chart(
    df_rank_hist: pd.DataFrame,
    player_name: str,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last: int | None = 15,
    temporal_time_scale: bool = False,
) -> alt.Chart:
    # Clean df
    max_rank = int(df_rank_hist["rank"].max())
    df_hist = df_rank_hist.query(f"player_name == '{player_name}'")
    col_to_keep = ["date", "rank"]
    df_hist = df_hist[col_to_keep].copy()
    df_hist["date"] = pd.to_datetime(df_hist["date"])
    if limit_last:
        df_hist = df_hist.tail(limit_last)
    ## Rename to use user friendly/language names
    df_hist = df_hist.rename(columns=translator.dict_lang)
    # Plot
    x_type = "temporal" if temporal_time_scale else "ordinal"
    chart_base = alt.Chart(df_hist).mark_line(interpolate="step-after")
    chart = chart_base.encode(
        x=alt.X(
            translator("date"),
            type=x_type,
            timeUnit="yearmonthdatehoursminutes",
            title=translator("date"),
        ),
        y=alt.Y(
            translator("rank") + ":Q",
            scale=alt.Scale(reverse=True, domain=(1, max_rank), nice=False, zero=False),
            axis=alt.Axis(values=list(range(1, max_rank + 1)), format="d"),
        ),
        tooltip=[translator("date"), translator("rank")],
    )
    return chart


def make_player_metric_history_chart(
    player_name: str,
    df_elo_hist: pd.DataFrame,
    df_matches: pd.DataFrame,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
    df_events: pd.DataFrame = None,
) -> None:
    # Metric selection
    list_metrics = [
        translator("elo_rating"),
        translator("nb_won_games_diff"),
        translator("rank"),
    ]
    metric = st.pills(
        label=translator("metric"),
        options=list_metrics,
        default=translator("nb_won_games_diff"),
    )
    # Gen chart
    if metric in (translator("elo_rating"), translator("nb_won_games_diff")):
        chart = _generate_player_metric_history_chart(
            player_name=player_name,
            metric=metric,
            df_elo_hist=df_elo_hist,
            df_matches=df_matches,
            translator=translator,
            limit_last_matches=limit_last_matches,
        )
    elif metric == translator("rank"):
        # Fetch df_rank_hist
        update_cache_rank_hist_current_league(session=None)
        # Go chart
        chart = _generate_player_rank_history_chart(
            df_rank_hist=st.session_state.df_rank_hist,
            player_name=player_name,
            translator=translator,
            limit_last=limit_last_matches,
        )
    else:
        raise NotImplementedError(
            f"{metric=} not in supported metrics ({list_metrics})"
        )
    ## Add events
    chart = add_events_to_chart(
        chart=chart,
        df_events=df_events,
        df_main=df_elo_hist,
        limit_last_matches=limit_last_matches,
        translator=translator,
    )
    # Plug it to Streamlit
    st.altair_chart(chart, width="stretch")


@st.cache_data(max_entries=32)
def _generate_team_metric_history_chart(
    team_name: str,
    df_matches: pd.DataFrame,
    metric: str = None,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
    temporal_time_scale: bool = False,
) -> alt.Chart:
    # Metric selection
    if metric is None:
        metric = translator("elo_rating")

    # Fetch data
    col_to_keep = ["date", "match_name", "result"]
    extra_tooltip = []
    if metric == translator("elo_rating"):
        # Fetch team elo history from DB
        with DB.get_session() as session:
            df_elo_hist = ranking_manager.get_team_elo_rating_histories(
                session=session,
                team_name=team_name,
                as_df=True,
            )
        df_hist = df_elo_hist.copy()  # .query(f"team_name == '{team_name}'").copy()
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
        df_hist = df_matches[df_matches["name"].str.contains(team_name)].copy()
        if limit_last_matches:
            df_hist = df_hist.tail(limit_last_matches)
        ## Determine result
        df_hist = df_hist.apply(
            _apply_determine_team_match_result,
            team_name=team_name,
            translator=translator,
            axis=1,
        )
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
        base_chart = alt.Chart(df_hist).mark_bar()
        y_domain = (df_hist[y_param].min() * 0.95, df_hist[y_param].max() * 1.05)
    elif metric == translator("nb_won_games_diff"):
        base_chart = alt.Chart(df_hist).mark_bar()
        y_domain = (0, df_hist[y_param].max() * 1.2)
    x_type = "temporal" if temporal_time_scale else "ordinal"
    chart = base_chart.encode(
        x=alt.X(
            x_param,
            type=x_type,
            timeUnit="yearmonthdatehoursminutes",
            title=translator("date"),
        ),
        y=alt.Y(y_param, scale=alt.Scale(domain=y_domain)),
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
    return chart


def make_team_metric_history_chart(
    team_name: str,
    df_matches: pd.DataFrame,
    translator: LanguageTranslator = DEFAULT_TRANSLATOR,
    limit_last_matches: int | None = 15,
    df_events: pd.DataFrame = None,
) -> None:
    # Metric selection
    metric = st.pills(
        label=translator("metric"),
        options=[translator("elo_rating"), translator("nb_won_games_diff")],
        default=translator("elo_rating"),
    )
    # Gen chart
    chart = _generate_team_metric_history_chart(
        team_name=team_name,
        metric=metric,
        df_matches=df_matches,
        translator=translator,
        limit_last_matches=limit_last_matches,
    )
    chart = add_events_to_chart(
        chart=chart,
        df_events=df_events,
        df_main=df_matches,
        limit_last_matches=limit_last_matches,
        translator=translator,
    )
    # Plug it to Streamlit
    st.altair_chart(chart, width="stretch")
