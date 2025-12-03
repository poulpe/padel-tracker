import streamlit as st

from padel_tracker.utils.datetime_utils import make_datetime_from_combi
from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import (
    PlayerNotFoundError,
    SamePlayerInBothTeamsError,
    SamePlayerInOneTeamError,
    PlayerNotInLeagueError,
)
from padel_tracker.database.db import DB
from padel_tracker.services import match_manager, player_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.languages import get_translator
from padel_tracker.ui.threads import get_thread_pool

# Init pages
## General
LOGGER = get_logger("ui.page_delete_match")
translator = get_translator()

## add match player names variables in st.session_state
for var in ["del_match_t1_p1", "del_match_t1_p2", "del_match_t2_p1", "del_match_t2_p2"]:
    if var not in st.session_state:
        st.session_state[var] = None

player_names = st.session_state.player_names

# Page header
st.write("")
write_header(translator("delete_match"))

# Forms
## Retrieve match if no known id
write_subheader(translator("retrieve_match"))
with st.form(translator("retrieve_match")):
    # Player selection
    col_team1, col_team2 = st.columns(2, border=True)
    with col_team1:
        write_subheader(translator("team1"), bold=True)
        st.selectbox(
            label="team1_player1_name",
            options=player_names,
            placeholder=translator("player1"),
            label_visibility="hidden",
            key="del_match_t1_p1",
            index=(
                player_names.index(st.session_state["del_match_t1_p1"])
                if st.session_state["del_match_t1_p1"]
                else None
            ),
        )
        st.selectbox(
            label="team1_player2_name",
            options=player_names,
            placeholder=translator("player2"),
            label_visibility="hidden",
            key="del_match_t1_p2",
            index=(
                player_names.index(st.session_state["del_match_t1_p2"])
                if st.session_state["del_match_t1_p2"]
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
            key="del_match_t2_p1",
            index=(
                player_names.index(st.session_state["del_match_t2_p1"])
                if st.session_state["del_match_t2_p1"]
                else None
            ),
        )
        st.selectbox(
            label="team2_player2_name",
            options=player_names,
            placeholder=translator("player2"),
            label_visibility="hidden",
            key="del_match_t2_p2",
            index=(
                player_names.index(st.session_state["del_match_t2_p2"])
                if st.session_state["del_match_t2_p2"]
                else None
            ),
        )
    # Date selection
    _, date_col, time_col, _ = st.columns([1, 1, 1, 1])
    with date_col:
        date = st.date_input(translator("date"), format="DD/MM/YYYY")
    with time_col:
        time = st.time_input(translator("time"), value="18:30", step=1800)
    # Submit button
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button_no_id = st.form_submit_button(
            label=translator("delete"), width="stretch"
        )

## Form "ID is known"
write_subheader(translator("delete_match_from_id"))
with st.form(translator("delete_match_from_id")):
    match_id = st.text_input("match_id")
    _, col, _ = st.columns(3)
    with col:
        submit_button_id = st.form_submit_button(translator("delete"), width="stretch")

# Process if clicked
if submit_button_no_id or (submit_button_id and match_id):
    with DB.get_session() as session:
        try:
            # Fetch id if not given
            if submit_button_no_id:
                LOGGER.debug("fetching teams")
                team1 = player_manager.get_team_from_players_name(
                    session=session,
                    player1_name=st.session_state["del_match_t1_p1"],
                    player2_name=st.session_state["del_match_t1_p2"],
                    league_name=st.session_state.league_name,
                    create_if_not_found=False,
                )
                team2 = player_manager.get_team_from_players_name(
                    session=session,
                    player1_name=st.session_state["del_match_t2_p1"],
                    player2_name=st.session_state["del_match_t2_p2"],
                    league_name=st.session_state.league_name,
                    create_if_not_found=False,
                )
                match = match_manager.get_match(
                    session=session,
                    teams=[team1, team2],
                    league_name=st.session_state.league_name,
                    date=make_datetime_from_combi(date, time),
                )
                match_id = match.id
                st.info(
                    f"{translator("match_retrieved")} : id={match_id}, {match.name} : {match.score}",
                    icon="✔️",
                )
            # Launch match deletion
            match_manager.delete_match(
                session=session, match_id=match_id, thread_pool=get_thread_pool()
            )
            st.success(f"{translator('match_deleted')} (id={match_id} )", icon="☠️")
        except PlayerNotFoundError:
            st.error(f"{translator('match_already_deleted')}", icon="💥")
        except SamePlayerInBothTeamsError:
            st.error(translator("same_player_in_both_teams_error"), icon="💢")
        except SamePlayerInOneTeamError:
            st.error(translator("team_same_player_error"), icon="💢")
        except PlayerNotInLeagueError:
            st.error(translator("all_players_not_in_league_error"), icon="💢")
            refresh_cache()
        except Exception as exc:
            st.error(f"{translator('match_deletion_error')}: {exc}", icon="💥")
    refresh_cache(threaded=True)
