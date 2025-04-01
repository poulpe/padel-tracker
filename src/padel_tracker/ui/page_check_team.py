import streamlit as st

from padel_tracker.models.players import Team
from padel_tracker.services.player_manager import (
    get_team_black_beast_and_favorite_victim,
)
from padel_tracker.ui.cache import check_not_empty_database_matches
from padel_tracker.ui.cards import make_match_cards, display_team_relationships
from padel_tracker.ui.charts import make_team_metric_history_chart
from padel_tracker.ui.tables import make_team_overview_table
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.ui.headers import write_header, write_subheader

st.write("")
check_not_empty_database_matches()

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

write_header(translator("check_team"))

# Team selectform
form = st.form("check_team")
with form:
    _, col1, col2, _ = st.columns([1, 2, 2, 1])
    with col1:
        player1_name = st.selectbox(
            label=translator("player1"),
            options=st.session_state.player_names,
            placeholder="",
            index=None,
        )
    with col2:
        player2_name = st.selectbox(
            label=translator("player2"),
            options=st.session_state.player_names,
            placeholder="",
            index=None,
        )
    _, col_center, _ = st.columns([1, 3, 1])
    with col_center:
        submit_button = st.form_submit_button(
            label=translator("submit"),
            use_container_width=True,
        )

# Checks and store selected_team in session_state
if submit_button:
    if (not player1_name) or (not player2_name):
        st.error(translator("player_not_selected_error"), icon="💢")
        st.stop()
    if player1_name == player2_name:
        st.error(translator("team_same_player_error"), icon="💢")
        st.stop()
    # OK, create team
    team_name = Team.get_name_from_players_name(player1_name, player2_name)
    st.session_state["selected_team_name"] = team_name

# Display page
st.write("")
if "selected_team_name" in st.session_state and st.session_state["selected_team_name"]:
    # Prepare data
    team_name = st.session_state["selected_team_name"]
    df_teams = st.session_state.df_teams.copy()
    df_team = df_teams.query(f"name == '{team_name}'")
    if len(df_team) == 0:
        st.error(translator("team_not_found_error"), icon="💢")
        st.stop()
    else:
        df_matches = st.session_state.df_matches.copy()
        df_matches = df_matches[df_matches["name"].str.contains(team_name)]

    # Go display page
    write_header(team_name)

    # Checks data not empty
    if len(df_matches) == 0:
        st.warning(translator("no_match_database_error"), icon="💢")
        st.stop()

    # Overview card TODO (prio3): Cool display card ?
    write_subheader(translator("overview"))
    make_team_overview_table(
        df_teams=df_team,
        translator=translator,
        extra_col=True,
        is_single=True,
        use_container_width=True,
    )

    # Relationships related
    write_subheader(translator("player_relationships"))
    tuple_opponents = get_team_black_beast_and_favorite_victim(
        team_name=team_name,
        df_matches=df_matches,
    )
    black_beast = tuple_opponents[0]
    nb_defeats_black_beast = tuple_opponents[1]
    favorite_victim = tuple_opponents[2]
    nb_victories_favorite_victim = tuple_opponents[3]
    display_team_relationships(
        black_beast=black_beast,
        nb_defeats_black_beast=nb_defeats_black_beast,
        favorite_victim=favorite_victim,
        nb_victories_favorite_victim=nb_victories_favorite_victim,
        translator=translator,
    )

    # Team graph (team_elo_history)
    write_subheader(translator("evolution"))
    make_team_metric_history_chart(
        team_name=team_name,
        df_matches=df_matches,
        translator=translator,
        limit_last_matches=None,
    )

    # Matches history
    write_subheader(translator("match_history"))
    _, col_matches_cont, _ = st.columns([1, 4, 1])
    with col_matches_cont:
        matches_cont = st.container(border=True, height=900)
    with matches_cont:
        make_match_cards(df_matches=df_matches, limit_last=None)
