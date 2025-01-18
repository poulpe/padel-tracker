import streamlit as st

from padel_tracker.ui.charts import make_DUMMY_overview_elo_history_chart
from padel_tracker.ui.cards import display_match_card

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
        <div style="font-size: 30px; font-weight: bold; margin: 0;"> Billboard </div>
        <div style="font-size: 20px; margin: 0;"> Top of the pops </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True
)
make_DUMMY_overview_elo_history_chart()

# View last match history
st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: 30px; font-weight: bold; margin: 0;"> {st.session_state.translator("match_history")} </div>
    </div>
    """,
    unsafe_allow_html=True
)
_, col_matches_cont, _ = st.columns([1,4,1])

with col_matches_cont:
    matches_cont = st.container(border=True, height=400)

with matches_cont:
    #TOCHECK : display_match_card

    # Exemple d'affichage d'un match
    team1 = "ElPoulpo/Sergissimo"
    team2 = "Max/Biboono"
    date = "07/01/2025"
    games_set1_team1 = 3
    games_set1_team2 = 6
    games_set2_team1 = 4
    games_set2_team2 = 6
    games_set3_team1 = None
    games_set3_team2 = None

    display_match_card(
        team1=team1,
        team2=team2,
        team1_won=False,
        date=date,
        games_set1_team1=games_set1_team1,
        games_set1_team2=games_set1_team2,
        games_set2_team1=games_set2_team1,
        games_set2_team2=games_set2_team2,
        games_set3_team1=games_set3_team1,
        games_set3_team2=games_set3_team2,
    )
    display_match_card(
        team1=team1,
        team2=team2,
        team1_won=False,
        date=date,
        games_set1_team1=games_set1_team1,
        games_set1_team2=games_set1_team2,
        games_set2_team1=games_set2_team1,
        games_set2_team2=games_set2_team2,
        games_set3_team1=games_set3_team1,
        games_set3_team2=games_set3_team2,
    )
    display_match_card(
        team1=team1,
        team2=team2,
        team1_won=True,
        date=date,
        games_set1_team1=games_set1_team1,
        games_set1_team2=games_set1_team2,
        games_set2_team1=games_set2_team1,
        games_set2_team2=games_set2_team2,
        games_set3_team1=games_set3_team1,
        games_set3_team2=games_set3_team2,
    )

# TODO : Player data table
