import streamlit as st

from padel_tracker.utils.datetime_utils import make_datetime_from_combi
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.models.matches import MatchScore
from padel_tracker.database.db import get_db_session
from padel_tracker.services.player_manager import (
    get_all_players,
    get_team_from_players_name,
)
from padel_tracker.services.match_manager import create_match, MatchExistsError

FONT_SIZE_HEADER = 30
FONT_SIZE_SUBHEADER = 20

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR

st.markdown(
    f"""
    <div style="text-align: center;">
        <div style="font-size: {FONT_SIZE_HEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("add_match")} </div>
        <br>
    </div>
    """,
    unsafe_allow_html=True,
)

form = st.form("add_match")
with form:
    # Get players list
    with get_db_session() as session:
        list_players = get_all_players(session=session)
        player_names = [p.name for p in list_players]

    # Player selection
    col_team1, col_team2 = st.columns(2, border=True)
    with col_team1:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: {FONT_SIZE_SUBHEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("team1")} </div>
                <br>
            </div>
            """,
            unsafe_allow_html=True,
        )
        team1_player1_name = st.selectbox(
            label="team1_player1_name",
            options=player_names,
            placeholder=st.session_state.translator("player1"),
            index=None,
            label_visibility="hidden",
        )
        team1_player2_name = st.selectbox(
            label="team1_player2_name",
            options=player_names,
            placeholder=st.session_state.translator("player2"),
            index=None,
            label_visibility="hidden",
        )
    with col_team2:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: {FONT_SIZE_SUBHEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("team2")} </div>
                <br>
            </div>
            """,
            unsafe_allow_html=True,
        )
        team2_player1_name = st.selectbox(
            label="team2_player1_name",
            options=player_names,
            placeholder=st.session_state.translator("player1"),
            index=None,
            label_visibility="hidden",
        )
        team2_player2_name = st.selectbox(
            label="team2_player2_name",
            options=player_names,
            placeholder=st.session_state.translator("player2"),
            index=None,
            label_visibility="hidden",
        )

    # Date selection
    _, date_col, time_col, _ = st.columns([1, 1, 1, 1])
    with date_col:
        date = st.date_input(st.session_state.translator("date"), format="DD/MM/YYYY")
    with time_col:
        time = st.time_input(st.session_state.translator("time"), value="18:30")

    # Score input
    _, col_set1_title, col_set2_title, col_set3_title = st.columns(
        [0.4, 0.2, 0.2, 0.2], vertical_alignment="bottom"
    )
    with col_set1_title:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <br>
                <div style="font-size: {16}px; margin: 0;">Set 1</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_set2_title:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <br>
                <div style="font-size: {16}px; margin: 0;">Set 2</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_set3_title:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <br>
                <div style="font-size: {16}px; margin: 0;">Set 3</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col_teams, col_set1, col_set2, col_set3 = st.columns(
        [0.4, 0.2, 0.2, 0.2], vertical_alignment="top"
    )
    with col_teams:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <br>
                <div style="font-size: {FONT_SIZE_SUBHEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("team1")} </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: {FONT_SIZE_SUBHEADER}px; font-weight: bold; margin: 0;"> {st.session_state.translator("team2")} </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_set1:
        games_set1_team1 = st.number_input(
            "games_set1_team1",
            value=None,
            min_value=0,
            max_value=7,
            step=1,
            format="%i",
            label_visibility="hidden",
        )
        games_set1_team2 = st.number_input(
            "games_set1_team2",
            value=None,
            min_value=0,
            max_value=7,
            step=1,
            format="%i",
            label_visibility="hidden",
        )
    with col_set2:
        games_set2_team1 = st.number_input(
            "games_set2_team1",
            value=None,
            min_value=0,
            max_value=7,
            step=1,
            format="%i",
            label_visibility="hidden",
        )
        games_set2_team2 = st.number_input(
            "games_set2_team2",
            value=None,
            min_value=0,
            max_value=7,
            step=1,
            format="%i",
            label_visibility="hidden",
        )
    with col_set3:
        games_set3_team1 = st.number_input(
            "games_set3_team1",
            value=None,
            min_value=0,
            max_value=10,
            step=1,
            format="%i",
            label_visibility="hidden",
        )
        games_set3_team2 = st.number_input(
            "games_set3_team2",
            value=None,
            min_value=0,
            max_value=10,
            step=1,
            format="%i",
            label_visibility="hidden",
        )

    # with col_set1:
    #     games_set1_team1 = st.text_input("games_set1_team1", value=None, label_visibility="hidden")
    #     games_set1_team2 = st.text_input("games_set1_team2", value=None, label_visibility="hidden")
    # with col_set2:
    #     games_set2_team1 = st.text_input("games_set2_team1", value=None, label_visibility="hidden")
    #     games_set2_team2 = st.text_input("games_set2_team2", value=None, label_visibility="hidden")
    # with col_set3:
    #     games_set3_team1 = st.text_input("games_set3_team1", value=None,  label_visibility="hidden")
    #     games_set3_team2 = st.text_input("games_set3_team2", value=None,  label_visibility="hidden")

    st.write("")
    st.write("")

    # Submit button
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=st.session_state.translator("submit"), use_container_width=True
        )

# Create match if submitted
if submit_button:
    match_datetime = make_datetime_from_combi(date, time)
    match_score = MatchScore(
        games_set1_team1=games_set1_team1,
        games_set1_team2=games_set1_team2,
        games_set2_team1=games_set2_team1,
        games_set2_team2=games_set2_team2,
        games_set3_team1=games_set3_team1,
        games_set3_team2=games_set3_team2,
    )
    with get_db_session() as session:
        team1 = get_team_from_players_name(
            session=session,
            player1_name=team1_player1_name,
            player2_name=team1_player2_name,
            create_if_not_found=True,
        )
        team2 = get_team_from_players_name(
            session=session,
            player1_name=team2_player1_name,
            player2_name=team2_player2_name,
            create_if_not_found=True,
        )
        try:
            create_match(
                session=session,
                teams=[team1, team2],
                date=match_datetime,
                score=match_score,
            )
            st.success(st.session_state.translator("match_added_success"), icon="🔥")
        except MatchExistsError:
            st.error(st.session_state.translator("match_exists_error"), icon="💢")
        except Exception as exc:
            st.error(
                f"{st.session_state.translator("match_added_error")}: {exc}", icon="💥"
            )
