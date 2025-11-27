import streamlit as st

from padel_tracker.utils.errors import PlayerExistsError, InvalidPlayerNameError
from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager
from padel_tracker.ui.cache import refresh_cache
from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import get_translator

st.write("")

translator = get_translator()

write_header(translator("add_player_in_league"))

form = st.form("add_player_in_league")
with form:
    _, center_col, _ = st.columns([1, 5, 1])
    with center_col:
        player_name = st.text_input(translator("name"))
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        submit_button = st.form_submit_button(
            label=translator("submit"),
            width="stretch",
        )

if submit_button:
    try:
        with DB.get_session() as session:
            # Fetch league
            league = league_manager.get_league_from_name(
                session=session, name=st.session_state.league_name
            )
            player_manager.create_player(
                session=session, name=player_name, league=league
            )
            st.success(f"{player_name}{translator("player_added_success")}", icon="🔥")
    except PlayerExistsError:
        st.error(f"{player_name}{translator("player_exists_error")}", icon="💢")
    except InvalidPlayerNameError:
        st.error(f"{player_name}{translator("player_invalid_name_error")}", icon="💢")
    except Exception as exc:
        st.error(f"{translator("player_added_error")}: {exc}", icon="💥")
    else:
        refresh_cache(threaded=True)

##########################################3

# form = st.form("add_existing_in_league")
# with form:
#     write_subheader(translator("add_existing_in_league"))
#     _, center_col, _ = st.columns([1, 5, 1])
#     with center_col:
#         with DB.get_session() as session:
#             other_players = player_manager.get_all_players_names_from_other_leagues(
#                 session=session,
#                 league_name_exclude=st.session_state.league_name,
#             )
#         player_name = st.selectbox(
#             label=translator("player_name"),
#             options=other_players,
#             placeholder=translator("player"),
#         )
#     _, center_col, _ = st.columns([1, 2, 1])
#     with center_col:
#         add_submit_button = st.form_submit_button(
#             label=translator("submit"),
#             width="stretch",
#         )
# if add_submit_button:
#     try:
#         with DB.get_session() as session:
#             player = player_manager.get_player_from_name(
#                 session=session, name=player_name
#             )
#             league = league_manager.get_league_from_name(
#                 session=session, name=league_name,
#             )
#             league_manager.assign_league_to_player(
#                 session=session, player=player, league=league
#             )
#         st.success(
#             f"{player_name}{translator("assigned_league_to_player_success")}{league_name}",
#             icon="🔥",
#         )
#     except PlayerAlreadyInLeagueError:
#         st.error(
#             f"{player_name}{translator("player_already_in_league_error")}{league_name}",
#             icon="💢",
#         )
#     except Exception as exc:
#         st.error(f"{translator("player_added_error")}: {exc}", icon="💥")
#     else:
#         refresh_cache(threaded=True)
#
# ## FORM Declare new player in league
# form = st.form("add_player_in_league")
# with form:
#     write_subheader(translator("add_player_in_league"))
#     _, center_col, _ = st.columns([1, 5, 1])
#     with center_col:
#         player_name = st.text_input(translator("name"))
#     _, center_col, _ = st.columns([1, 2, 1])
#     with center_col:
#         add_new_submit_button = st.form_submit_button(
#             label=translator("submit"),
#             width="stretch",
#         )
# if add_new_submit_button:
#     try:
#         with DB.get_session() as session:
#             league = league_manager.get_league_from_name(
#                 session=session, name=league_name,
#             )
#             player_manager.create_player(
#                 session=session, name=player_name, league=league
#             )
#             st.success(
#                 f"{player_name}{translator("player_added_success")}", icon="🔥"
#             )
#     except PlayerExistsError:
#         st.error(f"{player_name}{translator("player_exists_error")}", icon="💢")
#     except InvalidPlayerNameError:
#         st.error(
#             f"{player_name}{translator("player_invalid_name_error")}", icon="💢"
#         )
#     except Exception as exc:
#         st.error(f"{translator("player_added_error")}: {exc}", icon="💥")
#     else:
#         refresh_cache(threaded=False)
