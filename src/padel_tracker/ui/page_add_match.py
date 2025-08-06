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
from padel_tracker.ui.languages import get_translator
from padel_tracker.ui.cards import display_elo_rating_gains_metrics
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.cache import refresh_cache, check_not_empty_database_players
from padel_tracker.ui.threads import get_thread_pool

LOGGER = get_logger("ui.page_add_match")

st.write("")
check_not_empty_database_players()

translator = get_translator()

write_header(translator("add_match"))

# Init add match player names variables in st.session_state
for var in ["add_match_t1_p1", "add_match_t1_p2", "add_match_t2_p1", "add_match_t2_p2"]:
    if var not in st.session_state:
        st.session_state[var] = None

player_names = st.session_state.player_names

with st.form("add_match"):
    # Player selection
    col_team1, col_team2 = st.columns(2, border=True)
    with col_team1:
        write_subheader(translator("team1"), bold=True)
        st.selectbox(
            label="team1_player1_name",
            options=player_names,
            placeholder=translator("player1"),
            label_visibility="hidden",
            key="add_match_t1_p1",
            index=(
                player_names.index(st.session_state["add_match_t1_p1"])
                if st.session_state["add_match_t1_p1"]
                else None
            ),
        )
        st.selectbox(
            label="team1_player2_name",
            options=player_names,
            placeholder=translator("player2"),
            label_visibility="hidden",
            key="add_match_t1_p2",
            index=(
                player_names.index(st.session_state["add_match_t1_p2"])
                if st.session_state["add_match_t1_p2"]
                else None
            ),
        )
    with col_team2:
        write_subheader(translator("team2"), bold=True)
        st.selectbox(
            label="team2_player1_name",
            options=player_names,
            placeholder=translator("player1"),
            label_visibility="hidden",
            key="add_match_t2_p1",
            index=(
                player_names.index(st.session_state["add_match_t2_p1"])
                if st.session_state["add_match_t2_p1"]
                else None
            ),
        )
        st.selectbox(
            label="team2_player2_name",
            options=player_names,
            placeholder=translator("player2"),
            label_visibility="hidden",
            key="add_match_t2_p2",
            index=(
                player_names.index(st.session_state["add_match_t2_p2"])
                if st.session_state["add_match_t2_p2"]
                else None
            ),
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
        team_word: st.column_config.TextColumn(pinned=True, required=True, validate=fr"^{team_word}[12]$", disabled=True),
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

# Launch processing once clicked
if submit_button:
    team1_player1_name = st.session_state["add_match_t1_p1"]
    team1_player2_name = st.session_state["add_match_t1_p2"]
    team2_player1_name = st.session_state["add_match_t2_p1"]
    team2_player2_name = st.session_state["add_match_t2_p2"]
    # Check all players have been fulfilled
    if (not team1_player1_name) or (not team1_player2_name):
        st.error(translator("player_not_selected_error"), icon="💢")
        st.stop()
    elif (not team2_player1_name) or (not team2_player2_name):
        st.error(translator("player_not_selected_error"), icon="💢")
        st.stop()
    # Checks Score have been fulfilled
    try:
        match_score = MatchScore(
            games_set1_team1=games_set1_team1,
            games_set1_team2=games_set1_team2,
            games_set2_team1=games_set2_team1,
            games_set2_team2=games_set2_team2,
            games_set3_team1=games_set3_team1,
            games_set3_team2=games_set3_team2,
        )
        if not match_score.is_match_finished():
            raise MatchNotFinishedError
    except (ValidationError, ValueError, MatchNotFinishedError):
        st.error(translator("match_not_finished_error"), icon="💢")
        st.stop()
    except Exception as exc:
        err_msg = f"{translator("match_not_finished_error")}: {exc}"
        st.error(err_msg, icon="💢")
        st.stop()
    # Go create match
    LOGGER.debug("launching match creation")
    match_datetime = make_datetime_from_combi(date, time)
    is_success = False
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
            st.error(f"{translator("match_added_error")}: {exc}", icon="💥")
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
                _, center_col, _ = st.columns(3)
                with center_col:
                    st.write(translator("see_updated_elo_below"))
                dict_gains, dict_updated_ratings = process_finished_match(
                    session=session,
                    match=match,
                    delete_on_error=True,
                    thread_pool=get_thread_pool(),
                )
                display_elo_rating_gains_metrics(dict_gains, dict_updated_ratings)
                LOGGER.debug("finished processing")
            except MatchExistsError:
                st.error(translator("match_exists_error"), icon="💢")
            except MatchNotFinishedError:
                st.error(translator("match_not_finished_error"), icon="💢")
            except SamePlayerInBothTeamsError:
                st.error(translator("same_player_in_both_teams_error"), icon="💢")
            except PlayerNotInLeagueError:
                st.error(translator("all_players_not_in_league_error"), icon="💢")
                refresh_cache()
            except Exception as exc:
                st.error(f"{translator("match_added_error")}: {exc}", icon="💥")
            else:
                is_success = True

    # Refresh cache outside of the previous db_session
    if is_success:
        refresh_cache(threaded=True)
