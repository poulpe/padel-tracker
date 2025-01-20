import streamlit as st
import pandas as pd
from pydantic import ValidationError

from padel_tracker.utils.datetime_utils import make_datetime_from_combi
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.models.matches import MatchScore
from padel_tracker.database.db import get_db_session
from padel_tracker.services.player_manager import (
    get_all_players,
    get_team_from_players_name,
    SamePlayerInOneTeamError,
)
from padel_tracker.services.match_manager import (
    create_match,
    MatchExistsError,
    MatchNotFinishedError,
    SamePlayerInBothTeamsError,
)

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
        team1_word = st.session_state.translator("team1")
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: {FONT_SIZE_SUBHEADER}px; font-weight: bold; margin: 0;"> {team1_word} </div>
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
        team2_word = st.session_state.translator("team2")
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: {FONT_SIZE_SUBHEADER}px; font-weight: bold; margin: 0;"> {team2_word} </div>
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

    # Score input as df
    score_word = st.session_state.translator("score")
    team_word = st.session_state.translator("team")
    df = pd.DataFrame(
        [
            {team_word: f"{team_word} 1", "Set 1": None, "Set 2": None, "Set 3": None},
            {team_word: f"{team_word} 2", "Set 1": None, "Set 2": None, "Set 3": None},
        ]
    )
    df = df.set_index(team_word)
    # fmt: off
    column_config = {
        team_word: st.column_config.TextColumn(pinned=True, required=True, validate=fr"^{team_word} [12]$"),
        "Set 1": st.column_config.NumberColumn(default=None, format="%i", min_value=0, max_value=7, step=1, required=True),
        "Set 2": st.column_config.NumberColumn(default=None, format="%i", min_value=0, max_value=7, step=1),
        "Set 3": st.column_config.NumberColumn(default=None, format="%i", min_value=0, max_value=10, step=1),
    }
    # fmt: on
    _, center_col, _ = st.columns([1, 2.5, 1])
    with center_col:
        score_cont = st.container(border=True)
        with score_cont:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: {FONT_SIZE_SUBHEADER}px; font-weight: bold; margin: 0;"> {score_word} </div>
                    <br>
                </div>
                """,
                unsafe_allow_html=True,
            )
            df_score = st.data_editor(
                df, use_container_width=True, column_config=column_config
            )
            games_set1_team1 = df_score.at[f"{team_word} 1", "Set 1"]
            games_set1_team2 = df_score.at[f"{team_word} 2", "Set 1"]
            games_set2_team1 = df_score.at[f"{team_word} 1", "Set 2"]
            games_set2_team2 = df_score.at[f"{team_word} 2", "Set 2"]
            games_set3_team1 = df_score.at[f"{team_word} 1", "Set 3"]
            games_set3_team2 = df_score.at[f"{team_word} 2", "Set 3"]

    # Date selection
    _, date_col, time_col, _ = st.columns([1, 1, 1, 1])
    with date_col:
        date = st.date_input(st.session_state.translator("date"), format="DD/MM/YYYY")
    with time_col:
        time = st.time_input(st.session_state.translator("time"), value="18:30")

    st.write("")

    # Submit button
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=st.session_state.translator("submit"), use_container_width=True
        )

# Checks Players have been fulfilled
is_players_all_fulfilled = True
if submit_button:
    if (not team1_player1_name) or (not team1_player2_name):
        st.error(st.session_state.translator("player_not_selected_error"), icon="💢")
        is_players_all_fulfilled = False
    elif (not team2_player1_name) or (not team2_player2_name):
        st.error(st.session_state.translator("player_not_selected_error"), icon="💢")
        is_players_all_fulfilled = False

# Checks Score have been fulfilled
is_score_validated = False
match_score = None
if submit_button and is_players_all_fulfilled:
    try:
        match_score = MatchScore(
            games_set1_team1=games_set1_team1,
            games_set1_team2=games_set1_team2,
            games_set2_team1=games_set2_team1,
            games_set2_team2=games_set2_team2,
            games_set3_team1=games_set3_team1,
            games_set3_team2=games_set3_team2,
        )
        is_score_validated = True
    except ValidationError:
        st.error(st.session_state.translator("match_not_finished_error"), icon="💢")
    except Exception as exc:
        st.error(
            f"{st.session_state.translator("match_not_finished_error")}: {exc}",
            icon="💢",
        )

# Create match if submitted
if submit_button and is_players_all_fulfilled and is_score_validated:
    # Go create match
    match_datetime = make_datetime_from_combi(date, time)
    with get_db_session() as session:
        try:
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
        except SamePlayerInOneTeamError:
            st.error(st.session_state.translator("team_same_player_error"), icon="💢")
        except Exception as exc:
            st.error(
                f"{st.session_state.translator("match_added_error")}: {exc}", icon="💥"
            )
        else:
            try:
                create_match(
                    session=session,
                    teams=[team1, team2],
                    date=match_datetime,
                    score=match_score,
                )
                st.success(
                    st.session_state.translator("match_added_success"), icon="🔥"
                )
            except MatchExistsError:
                st.error(st.session_state.translator("match_exists_error"), icon="💢")
            except MatchNotFinishedError:
                st.error(
                    st.session_state.translator("match_not_finished_error"), icon="💢"
                )
            except SamePlayerInBothTeamsError:
                st.error(
                    st.session_state.translator(
                        "match_same_player_in_both_teams_error"
                    ),
                    icon="💢",
                )
            except Exception as exc:
                st.error(
                    f"{st.session_state.translator("match_added_error")}: {exc}",
                    icon="💥",
                )
