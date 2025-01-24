import streamlit as st

from padel_tracker.ui.charts import make_overview_elo_history_chart
from padel_tracker.ui.cards import make_match_cards
from padel_tracker.ui.tables import make_player_overview_table

FONT_SIZE_HEADER = 30
FONT_SIZE_SUBHEADER = 20

st.write("")
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
        st.session_state.translator("add_player"),
        type="primary",
        use_container_width=True,
    )

if button_add_match:
    st.switch_page("page_add_match.py")
if button_feature_2:
    st.switch_page("page_add_player.py")

st.write("")
st.write("")

# Overview chart
make_overview_elo_history_chart(translator=st.session_state.translator, font_size_header=FONT_SIZE_HEADER, font_size_subheader=FONT_SIZE_SUBHEADER)

# Player data table overview
#st.write("")
st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: {FONT_SIZE_HEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("players_table")} </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True,
)
make_player_overview_table(translator=st.session_state.translator)

# View last match history
st.write("")
st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: {FONT_SIZE_HEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("last_match_history")} </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True,
)
_, col_matches_cont, _ = st.columns([1, 4, 1])

with col_matches_cont:
    matches_cont = st.container(border=True, height=600)
with matches_cont:
    make_match_cards(limit_last=8)


