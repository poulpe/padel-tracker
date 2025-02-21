import streamlit as st

from padel_tracker.ui.tables import (
    make_player_overview_table,
    make_league_overview_table,
)
from padel_tracker.utils.errors import PlayerAlreadyInLeagueError
from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

write_header(translator("manage_league"))

# Fetch current league
league_name = st.session_state.league_name
query_name = f"name == '{league_name}'"
df_league = st.session_state.df_leagues.query(query_name).reset_index(drop=True).copy()
df_players = st.session_state.df_players.copy()

# Show league infos
if df_league["is_private"][0]:
    is_private_str = translator("private_league")
    is_private_icon = "🔒"
else:
    is_private_str = translator("public_league")
    is_private_icon = "🤗"
write_subheader(f"{is_private_str} {is_private_icon}", bold=False)
write_subheader(translator("description"), extra_line=False)
description = df_league["description"][0]
if not description:
    description = translator("no_description_yet")
write_subheader(description, bold=False)

## Display league_overview_table
make_league_overview_table(df_league=df_league, translator=translator, is_single=True)

## Display players list
if (df_players is not None) and (not df_players.empty):
    write_subheader(translator("players_table"))
    highlight_player_name = None
    if "user" in st.session_state and st.session_state.user is not None:
        player_id = st.session_state.user["player_id"]
        if player_id:
            highlight_player_name = st.session_state.user["name"]
    make_player_overview_table(
        df_players=df_players,
        df_linkplayerleague=st.session_state.df_linkplayerleague,
        translator=translator,
        highlight_player_name=highlight_player_name,
    )

# TODO: FORM Recruit in league form (add check user rights
form = st.form("add_in_league")
with form:
    write_subheader(translator("add_in_league"))
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        with DB.get_session() as session:
            names = player_manager.get_all_players_names_from_other_leagues(
                session=session, league_name_exclude=league_name
            )
        player_name = st.selectbox(
            label=translator("player_name"),
            options=names,
            placeholder=translator("player"),
            index=None,
        )
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        add_submit_button = st.form_submit_button(
            label=translator("submit"),
            use_container_width=True,
        )
if add_submit_button:
    try:
        with DB.get_session() as session:
            player = player_manager.get_player_from_name(
                session=session, name=player_name
            )
            league = league_manager.get_league_from_name(
                session=session,
                name=league_name,
            )
            league_manager.assign_league_to_player(
                session=session, player=player, league=league
            )
        st.success(
            f"{player_name}{translator("assigned_league_to_player_success")}{league_name}",
            icon="🔥",
        )
    except PlayerAlreadyInLeagueError:
        st.error(
            f"{player_name}{translator("player_already_in_league_error")}{league_name}",
            icon="💢",
        )
    except Exception as exc:
        st.error(f"{translator("player_added_error")}: {exc}", icon="💥")
    else:
        refresh_cache(threaded=True)


# TODO : form Remove player from league


# TODO: define league admins
