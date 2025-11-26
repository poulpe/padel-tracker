import streamlit as st

from padel_tracker.ui.charts import make_overview_elo_history_chart
from padel_tracker.ui.cards import make_match_cards
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import get_translator
from padel_tracker.ui.tables import (
    make_player_overview_table,
    make_download_as_csv_button,
)
from padel_tracker.ui.cache import (
    check_not_empty_database_matches,
    check_not_empty_database_leagues,
    check_user_has_default_league,
)
from padel_tracker.ui.login import determine_is_guest

st.write("")

translator = get_translator()

check_not_empty_database_leagues()

# Top quick access buttons
is_guest = determine_is_guest()
if not is_guest:
    col_button_1, col_button_2 = st.columns([1, 1])
    with col_button_1:
        button_add_match = st.button(
            translator("add_match"),
            type="primary",
            use_container_width=True,
        )
    with col_button_2:
        button_feature_2 = st.button(
            translator("check_player"),
            type="primary",
            use_container_width=True,
        )
    if button_add_match:
        st.switch_page("page_add_match.py")
else:
    _, col_button_2, _ = st.columns([1, 3, 1])
    with col_button_2:
        button_feature_2 = st.button(
            translator("check_player"),
            type="primary",
            use_container_width=True,
        )

if button_feature_2:
    st.switch_page("page_check_player.py")

check_not_empty_database_matches()
check_user_has_default_league()

st.write("")
st.write("")

# Overview chart
nb_last_matches = 50
subtitle = translator("ranking_evolution_over_x_last_matches").format(x=nb_last_matches)
write_header(translator("billboard"), subtitle, bold_subheader=False)
make_overview_elo_history_chart(
    df_elo_hist=st.session_state.df_elo_hist,
    translator=translator,
    limit_last_matches=nb_last_matches,
    df_events=st.session_state.df_events,
)

# Player data table overview
write_header(translator("players_table"))
highlight_player_name = None
if "user" in st.session_state and st.session_state.user is not None:
    player_id = st.session_state.user["player_id"]
    if player_id:
        highlight_player_name = st.session_state.user["name"]
make_player_overview_table(
    df_players=st.session_state.df_players,
    df_linkplayerleague=st.session_state.df_linkplayerleague,
    translator=translator,
    highlight_player_name=highlight_player_name,
)

# View last match history
st.write("")
write_header(translator("last_match_history"))
_, col_matches_cont, _ = st.columns([1, 4, 1])
with col_matches_cont:
    matches_cont = st.container(border=True, height=600)
with matches_cont:
    make_match_cards(df_matches=st.session_state.df_matches, limit_last=nb_last_matches)

# Download data
st.write("")
write_header(translator("download_data_as_csv"))
col_matches, col_elo_hist = st.columns(2)
with col_matches:
    make_download_as_csv_button(
        label=translator("match_history"),
        df=st.session_state.df_matches,
        file_name=f"{st.session_state.league_name}_match_history.csv",
        translator=translator,
    )
with col_elo_hist:
    make_download_as_csv_button(
        label=translator("elo_rating"),
        df=st.session_state.df_elo_hist,
        file_name=f"{st.session_state.league_name}_elo_history.csv",
        translator=translator,
    )
