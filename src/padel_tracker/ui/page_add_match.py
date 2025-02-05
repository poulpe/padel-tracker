import streamlit as st
import pandas as pd
from pydantic import ValidationError

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.datetime_utils import make_datetime_from_combi
from padel_tracker.utils.errors import (
    MatchExistsError,
    MatchNotFinishedError,
    SamePlayerInBothTeamsError,
    SamePlayerInOneTeamError,
    PlayerNotInLeagueError,
)
from padel_tracker.models.matches import MatchScore
from padel_tracker.database.db import DB
from padel_tracker.services.player_manager import get_team_from_players_name
from padel_tracker.services.match_manager import create_match, process_finished_match
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.ui.cards import display_elo_rating_gains_metrics
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.cache import refresh_cache, check_not_empty_database_players

LOGGER = get_logger("ui.page_add_match")

st.write("")
check_not_empty_database_players()

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

write_header(translator("add_match"))

form = st.form("add_match")
with form:
    # Get players list
    player_names = st.session_state.player_names

    # Player selection
    col_team1, col_team2 = st.columns(2, border=True)
    with col_team1:
        write_subheader(translator("team1"), bold=True)
        team1_player1_name = st.selectbox(
            label="team1_player1_name",
            options=player_names,
            placeholder=translator("player1"),
            index=None,
            label_visibility="hidden",
        )
        team1_player2_name = st.selectbox(
            label="team1_player2_name",
            options=player_names,
            placeholder=translator("player2"),
            index=None,
            label_visibility="hidden",
        )
    with col_team2:
        write_subheader(translator("team2"), bold=True)
        team2_player1_name = st.selectbox(
            label="team2_player1_name",
            options=player_names,
            placeholder=translator("player1"),
            index=None,
            label_visibility="hidden",
        )
        team2_player2_name = st.selectbox(
            label="team2_player2_name",
            options=player_names,
            placeholder=translator("player2"),
            index=None,
            label_visibility="hidden",
        )

    # Score input as df
    team_word = translator("team")
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
            write_subheader(translator("score"), bold=True)
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
        date = st.date_input(translator("date"), format="DD/MM/YYYY")
    with time_col:
        time = st.time_input(translator("time"), value="18:30", step=1800)

    st.write("")

    # Submit button
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=translator("submit"), use_container_width=True
        )

# Checks Players have been fulfilled
is_players_all_fulfilled = True
if submit_button:
    if (not team1_player1_name) or (not team1_player2_name):
        st.error(translator("player_not_selected_error"), icon="💢")
        is_players_all_fulfilled = False
    elif (not team2_player1_name) or (not team2_player2_name):
        st.error(translator("player_not_selected_error"), icon="💢")
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
        st.error(translator("match_not_finished_error"), icon="💢")
    except Exception as exc:
        err_msg = f"{translator("match_not_finished_error")}: {exc}"
        st.error(err_msg, icon="💢")

# Create match if submitted
if submit_button and is_players_all_fulfilled and is_score_validated:
    # TODO: show waiting screen/animations (loading bar, anecdoctes padel, phrases à la con)
    LOGGER.debug("launching match creation")
    # Go create match
    match_datetime = make_datetime_from_combi(date, time)
    with DB.get_session() as session:
        try:
            LOGGER.debug("fetching teams")
            team1 = get_team_from_players_name(
                session=session,
                player1_name=team1_player1_name,
                player2_name=team1_player2_name,
                league_name=st.session_state.league_name,
                create_if_not_found=True,
            )
            team2 = get_team_from_players_name(
                session=session,
                player1_name=team2_player1_name,
                player2_name=team2_player2_name,
                league_name=st.session_state.league_name,
                create_if_not_found=True,
            )
        except SamePlayerInOneTeamError:
            st.error(translator("team_same_player_error"), icon="💢")
        except Exception as exc:
            err_msg = f"{translator("match_added_error")}: {exc}"
            st.error(err_msg, icon="💥")
        else:
            try:
                LOGGER.debug("creating new match")
                match = create_match(
                    session=session,
                    teams=[team1, team2],
                    league_name=st.session_state.league_name,
                    date=match_datetime,
                    score=match_score,
                    is_finished=False,
                )
                st.success(translator("match_added_success"), icon="🔥")
                LOGGER.debug("created match, starting processing")
                # Processing and showing results
                dict_elo_rating_gains, dict_updated_elo_ratings = (
                    process_finished_match(
                        session=session,
                        match=match,
                        delete_on_error=True,
                        thread_pool=st.session_state.thread_pool,
                    )
                )
                LOGGER.debug("finished processing")
                _, center_col, _ = st.columns(3)
                with center_col:
                    st.write(translator("see_updated_elo_below"))
                display_elo_rating_gains_metrics(
                    dict_elo_rating_gains, dict_updated_elo_ratings
                )
            except MatchExistsError:
                st.error(translator("match_exists_error"), icon="💢")
            except MatchNotFinishedError:
                st.error(translator("match_not_finished_error"), icon="💢")
            except SamePlayerInBothTeamsError:
                st.error(translator("same_player_in_both_teams_error"), icon="💢")
            except PlayerNotInLeagueError:
                st.error(translator("all_players_not_in_league_error"), icon="💢")
            except Exception as exc:
                st.error(f"{translator("match_added_error")}: {exc}", icon="💥")
    # TODO: Update ranks (in thread)
    # TODO: Refresh cache (in thread)
    refresh_cache()  # thread_pool=st.session_state.thread_pool
