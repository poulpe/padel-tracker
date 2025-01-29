import streamlit as st
import pandas as pd
from pydantic import ValidationError

from padel_tracker.utils.datetime_utils import make_datetime_from_combi
from padel_tracker.models.matches import MatchScore
from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import (
    get_team_from_players_name,
    SamePlayerInOneTeamError,
)
from padel_tracker.services.match_manager import (
    create_match,
    MatchExistsError,
    MatchNotFinishedError,
    SamePlayerInBothTeamsError,
    process_finished_match,
)
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.ui.cards import display_elo_rating_gains_metrics
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.cache import refresh_cache

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR

write_header(st.session_state.translator("add_match"))

form = st.form("add_match")
with form:
    # Get players list
    player_names = list(st.session_state.df_players["name"])
    # with DB.get_session() as session:
    #     list_players = get_all_players(session=session)
    #     player_names = [p.name for p in list_players]

    # Player selection
    col_team1, col_team2 = st.columns(2, border=True)
    with col_team1:
        write_subheader(st.session_state.translator("team1"), bold=True)
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
        write_subheader(st.session_state.translator("team2"), bold=True)
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
    team_word = st.session_state.translator("team")
    df = pd.DataFrame(
        [
            {team_word: f"{team_word}1", "Set1": None, "Set2": None, "Set3": None},
            {team_word: f"{team_word}2", "Set1": None, "Set2": None, "Set3": None},
        ]
    )
    df = df.set_index(team_word)
    # fmt: off
    column_config = {
        team_word: st.column_config.TextColumn(pinned=True, required=True, validate=fr"^{team_word}[12]$"),
        "Set1": st.column_config.NumberColumn(default=None, width="small", format="%i", min_value=0, max_value=7, step=1, required=True),
        "Set2": st.column_config.NumberColumn(default=None, width="small", format="%i", min_value=0, max_value=7, step=1),
        "Set3": st.column_config.NumberColumn(default=None, width="small", format="%i", min_value=0, max_value=10, step=1),
    }
    # fmt: on
    _, center_col, _ = st.columns([1, 2.8, 1])
    with center_col:
        score_cont = st.container(border=True)
        with score_cont:
            write_subheader(st.session_state.translator("score"), bold=True)
            df_score = st.data_editor(
                df, use_container_width=True, column_config=column_config
            )
            games_set1_team1 = df_score.at[f"{team_word}1", "Set1"]
            games_set1_team2 = df_score.at[f"{team_word}2", "Set1"]
            games_set2_team1 = df_score.at[f"{team_word}1", "Set2"]
            games_set2_team2 = df_score.at[f"{team_word}2", "Set2"]
            games_set3_team1 = df_score.at[f"{team_word}1", "Set3"]
            games_set3_team2 = df_score.at[f"{team_word}2", "Set3"]

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
        err_msg = f"{st.session_state.translator("match_not_finished_error")}: {exc}"
        st.error(err_msg, icon="💢")

# Create match if submitted
if submit_button and is_players_all_fulfilled and is_score_validated:
    # Go create match
    match_datetime = make_datetime_from_combi(date, time)
    with DB.get_session() as session:
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
            err_msg = f"{st.session_state.translator("match_added_error")}: {exc}"
            st.error(err_msg, icon="💥")
        else:
            try:
                match = create_match(
                    session=session,
                    teams=[team1, team2],
                    date=match_datetime,
                    score=match_score,
                    is_finished=False,
                )
                dict_elo_rating_gains, dict_updated_elo_ratings = (
                    process_finished_match(
                        session=session, match=match, delete_on_error=True
                    )
                )
                success_msg = st.session_state.translator("match_added_success")
                st.success(success_msg, icon="🔥")
                _, center_col, _ = st.columns(3)
                with center_col:
                    st.write(st.session_state.translator("see_updated_elo_below"))
                display_elo_rating_gains_metrics(
                    dict_elo_rating_gains, dict_updated_elo_ratings
                )
            except MatchExistsError:
                st.error(st.session_state.translator("match_exists_error"), icon="💢")
            except MatchNotFinishedError:
                err_msg = st.session_state.translator("match_not_finished_error")
                st.error(err_msg, icon="💢")
            except SamePlayerInBothTeamsError:
                err_msg = st.session_state.translator("same_player_in_both_teams_error")
                st.error(err_msg, icon="💢")
            except Exception as exc:
                err_msg = f"{st.session_state.translator("match_added_error")}: {exc}"
                st.error(err_msg, icon="💥")
    refresh_cache()
