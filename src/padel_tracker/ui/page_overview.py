import streamlit as st

from padel_tracker.ui.charts import make_overview_elo_history_chart
from padel_tracker.ui.cards import make_match_cards
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.tables import make_player_overview_table
from padel_tracker.ui.cache import check_not_empty_database_matches

st.write("")

# Top quick access buttons
col_button_1, col_button_2 = st.columns([1, 1])

with col_button_1:
    button_add_match = st.button(
        st.session_state.translator("add_match"),
        type="primary",
        use_container_width=True,
    )
with col_button_2:
    button_feature_2 = st.button(
        st.session_state.translator("check_player"),
        type="primary",
        use_container_width=True,
    )

if button_add_match:
    st.switch_page("page_add_match.py")
if button_feature_2:
    st.switch_page("page_check_player.py")

check_not_empty_database_matches()

st.write("")
st.write("")

# Overview chart
nb_last_matches = 15
subtitle = st.session_state.translator("ranking_evolution_over_x_last_matches").format(
    x=nb_last_matches
)
write_header("Billboard", subtitle, bold_subheader=False)
make_overview_elo_history_chart(
    df_elo_hist=st.session_state.df_elo_hist,
    translator=st.session_state.translator,
    limit_last_matches=nb_last_matches,
)

# Player data table overview
# st.write("")
write_header(st.session_state.translator("players_table"))
make_player_overview_table(
    df_players=st.session_state.df_players, translator=st.session_state.translator
)

# View last match history
st.write("")
write_header(st.session_state.translator("last_match_history"))
_, col_matches_cont, _ = st.columns([1, 4, 1])
with col_matches_cont:
    matches_cont = st.container(border=True, height=600)
with matches_cont:
    make_match_cards(df_matches=st.session_state.df_matches, limit_last=nb_last_matches)
