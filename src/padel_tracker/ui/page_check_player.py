import streamlit as st

from padel_tracker.services.player_manager import (
    get_best_teammate,
    get_most_played_teammate,
    get_black_beast_and_favorite_victim,
)
from padel_tracker.ui.cards import make_match_cards, display_player_relationships
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.inputs import make_player_selectbox
from padel_tracker.ui.charts import make_player_metric_history_chart
from padel_tracker.ui.tables import make_player_overview_table
from padel_tracker.ui.cache import check_not_empty_database_matches

st.write("")
check_not_empty_database_matches()

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

write_header(translator("check_player"))

# Player select box
# TODO : pass "clicked_player_name" when player is clicked from link (before switch_page)
if "clicked_player_name" in st.session_state:
    player_name = st.session_state["clicked_player_name"]
else:
    player_name = None
player_name = make_player_selectbox(player_name)
st.write("")

if player_name:
    # Fetch all df needed (from all leagues if applicable)
    df_player = st.session_state.df_players.query(f"name == '{player_name}'").copy()
    df_teams = st.session_state.df_teams_all_leagues.copy()
    df_teams = df_teams[df_teams["name"].str.contains(player_name, na=False)]
    df_matches = st.session_state.df_matches_all_leagues.copy()
    df_matches = df_matches[df_matches["name"].str.contains(player_name, na=False)]
    df_elo_hist = st.session_state.df_elo_hist.copy()
    df_elo_hist = df_elo_hist.query(f"player_name == '{player_name}'").copy()
    df_linkplayerleague = st.session_state.df_linkplayerleague.query(
        f"player_name == '{player_name}'"
    ).copy()

    write_header(player_name)

    # Checks data not empty
    if (len(df_teams) == 0) or (len(df_matches) == 0):
        st.warning(translator("no_match_database_error"), icon="💢")
        st.stop()

    # Overview card TODO (prio3): Cool display card ?
    write_subheader(translator("overview"))
    make_player_overview_table(
        df_players=df_player,
        df_linkplayerleague=df_linkplayerleague,
        translator=translator,
        extra_col=True,
        is_single=True,
        use_container_width=True,
    )

    # Relationships related
    write_subheader(translator("player_relationships"))
    ## Best teammate
    best_teammate_name, nb_victories_best = get_best_teammate(
        df_teams=df_teams, player_name=player_name
    )
    ## Most frequent teammate (player with the most matches)
    most_teammate_name, nb_matches_most = get_most_played_teammate(
        df_teams=df_teams, player_name=player_name
    )
    ## Black Beast (player against lost the most) and favorite victim (player against win the most)
    tuple_opponents = get_black_beast_and_favorite_victim(
        player_name=player_name, df_matches=df_matches
    )
    black_beast = tuple_opponents[0]
    nb_defeats_black_beast = tuple_opponents[1]
    favorite_victim = tuple_opponents[2]
    nb_victories_favorite_victim = tuple_opponents[3]
    ## Render the players
    display_player_relationships(
        best_teammate_name=best_teammate_name,
        nb_victories_best=nb_victories_best,
        most_teammate_name=most_teammate_name,
        nb_matches_most=nb_matches_most,
        black_beast=black_beast,
        nb_defeats_black_beast=nb_defeats_black_beast,
        favorite_victim=favorite_victim,
        nb_victories_favorite_victim=nb_victories_favorite_victim,
        translator=translator,
    )
    st.write("")

    # Graph
    write_subheader(translator("evolution"))
    make_player_metric_history_chart(
        player_name=player_name,
        df_elo_hist=df_elo_hist,
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
