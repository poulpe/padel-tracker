import streamlit as st

from padel_tracker.utils.errors import (
    PlayerAlreadyInLeagueError,
    PlayerExistsError,
    InvalidPlayerNameError,
)
from padel_tracker.database.db import DB
from padel_tracker.models.users import UserRole
from padel_tracker.services import player_manager, league_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.languages import get_translator
from padel_tracker.ui.inputs import make_player_selectbox
from padel_tracker.ui.tables import (
    make_player_overview_table,
    make_league_overview_table,
)

st.write("")

translator = get_translator()

# Fetch current league and user
league_name = st.session_state.league_name
query_name = f"name == '{league_name}'"
df_league = st.session_state.df_leagues.query(query_name).reset_index(drop=True).copy()
df_players = st.session_state.df_players.copy()
if "user" in st.session_state:
    user = st.session_state.user
else:
    user = None

# Show league infos
write_header(league_name, extra_line=False)
if df_league["is_private"][0]:
    is_private_str = translator("private_league")
    is_private_icon = "🔒"
else:
    is_private_str = translator("public_league")
    is_private_icon = "🤗"
write_subheader(f"{is_private_str} {is_private_icon}", bold=False)
write_subheader(translator("description"), extra_line=False)
try:
    description = df_league["description"][0]
except KeyError:
    description = translator("no_description_yet")
else:
    if not description:
        description = translator("no_description_yet")
write_subheader(description, bold=False)

## Display league_overview_table
make_league_overview_table(df_league=df_league, translator=translator, is_single=True)

## Display players list
if (df_players is not None) and (not df_players.empty):
    write_subheader(translator("players_table"))
    highlight_player_name = None
    if user:
        player_id = user["player_id"]
        if player_id:
            highlight_player_name = user["name"]
    make_player_overview_table(
        df_players=df_players,
        df_linkplayerleague=st.session_state.df_linkplayerleague,
        translator=translator,
        highlight_player_name=highlight_player_name,
    )

## Display league admins
write_subheader(translator("league_admins"), extra_line=False)
write_subheader(", ".join(st.session_state.league_admins), bold=False)

# Check if user is in league admins
is_user_league_admin = (
    user and ("admin_leagues" in user.keys()) and (league_name in user["admin_leagues"])
)
is_user_admin = user and "role" in user.keys() and user["role"] == UserRole.ADMIN
if not (is_user_league_admin or is_user_admin):
    st.stop()

# ADMINISTRATION
write_header(translator("administration"))
# FORMS Add/Recruit in
left_col, right_col = st.columns(2)
## FORM Declare new player in league
with left_col:
    form = st.form("add_player_in_league")
    with form:
        write_subheader(translator("add_player_in_league"))
        _, center_col, _ = st.columns([1, 5, 1])
        with center_col:
            player_name = st.text_input(translator("name"))
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            add_new_submit_button = st.form_submit_button(
                label=translator("submit"),
                width="stretch",
            )
    if add_new_submit_button:
        try:
            with DB.get_session() as session:
                league = league_manager.get_league_from_name(session, league_name)
                player_manager.create_player(
                    session=session, name=player_name, league=league
                )
                st.success(
                    f"{player_name}{translator("player_added_success")}", icon="🔥"
                )
        except PlayerExistsError:
            st.error(f"{player_name}{translator("player_exists_error")}", icon="💢")
        except InvalidPlayerNameError:
            st.error(
                f"{player_name}{translator("player_invalid_name_error")}", icon="💢"
            )
        except Exception as exc:
            st.error(f"{translator("player_added_error")}: {exc}", icon="💥")
        else:
            refresh_cache(threaded=False)
## FORM Recruit existing in league
with right_col:
    form = st.form("add_existing_in_league")
    with form:
        write_subheader(translator("add_existing_in_league"))
        _, center_col, _ = st.columns([1, 5, 1])
        with center_col:
            with DB.get_session() as session:
                names = player_manager.get_all_players_names_from_other_leagues(
                    session=session, league_name_exclude=league_name
                )
                names += player_manager.get_all_players_names_without_league(
                    session=session
                )
            names = list(set(names))
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
                width="stretch",
            )
    if add_submit_button:
        try:
            with DB.get_session() as session:
                player = player_manager.get_player_from_name(
                    session=session, name=player_name
                )
                league = league_manager.get_league_from_name(session, league_name)
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

# FORM Remove player from league
form = st.form("remove_from_league")
with form:
    write_subheader(translator("remove_from_league"))
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        player_name = make_player_selectbox()
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        remove_submit_button = st.form_submit_button(
            label=translator("submit"),
            width="stretch",
        )
if remove_submit_button:
    try:
        with DB.get_session() as session:
            player = player_manager.get_player_from_name(
                session=session, name=player_name
            )
            league = league_manager.get_league_from_name(session, league_name)
            league_manager.remove_player_from_league(
                session=session, player=player, league=league
            )
        st.success(
            f"{player_name}{translator("player_removed")}",
            icon="🔥",
        )
    except Exception as exc:
        st.error(f"{translator("player_deletion_error")}: {exc}", icon="💥")
    else:
        refresh_cache(threaded=True)

# FORM Change league description
form = st.form("change_league_description")
with form:
    write_subheader(translator("change_league_description"))
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        new_description = st.text_area(
            translator("description"), value=description, max_chars=256
        )
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        change_description_submit_button = st.form_submit_button(
            label=translator("submit"),
            width="stretch",
        )
if change_description_submit_button:
    try:
        with DB.get_session() as session:
            league = league_manager.get_league_from_name(
                session=session,
                name=league_name,
            )
            league_manager.update_league_description(
                session=session,
                league=league,
                description=new_description,
            )
        st.success(translator("description_updated_success"), icon="🔥")
    except Exception as exc:
        st.error(f"{translator("unknown_error_update")}: {exc}", icon="💥")
    else:
        refresh_cache(threaded=True)

# TODO: FORM define league admins

# DANGER ZONE
# TODO (prio3): make league public/private FORM
# TODO (prio3): rename league FORM
