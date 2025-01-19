import streamlit as st

from padel_tracker.ui.charts import make_overview_elo_history_chart
from padel_tracker.ui.cards import make_match_cards
from padel_tracker.ui.tables import make_player_overview_table

FONT_SIZE_HEADER = 30
FONT_SIZE_SUBHEADER = 20

st.write("")
st.write("")

# Top quick access buttons
col_button_1, col_button_2 = st.columns([1,1])

with col_button_1:
    button_add_match = st.button(st.session_state.translator("add_match"), type="primary", use_container_width=True)
with col_button_2:
    button_feature_2 = st.button(st.session_state.translator("next_feature"), type="primary", use_container_width=True)

if button_add_match:
    st.switch_page("page_add_match.py")
if button_feature_2:
    pass

st.write("")
st.write("")

# Overview chart
st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: {FONT_SIZE_HEADER}px; font-weight: bold; margin: 0;"> Billboard </div>
        <div style="font-size: {FONT_SIZE_SUBHEADER}px; margin: 0;"> Top of the pops </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True
)
#make_DUMMY_overview_elo_history_chart()
make_overview_elo_history_chart(translator=st.session_state.translator)

# View last match history
st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: {FONT_SIZE_HEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("match_history")} </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True
)
_, col_matches_cont, _ = st.columns([1,4,1])

with col_matches_cont:
    matches_cont = st.container(border=True, height=400)

with matches_cont:
    make_match_cards(limit_last=6)

# Player data table overview
st.write("")
st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: {FONT_SIZE_HEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("players_table")} </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True
)

make_player_overview_table(translator=st.session_state.translator)
