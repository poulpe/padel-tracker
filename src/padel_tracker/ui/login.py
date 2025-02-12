import streamlit as st

from padel_tracker.utils.errors import InvalidPlayerNameError
from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager, user_manager
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.languages import LanguageTranslator
from padel_tracker.ui.cache import refresh_cache, ALL_CACHE_KEYS


def determine_is_guest() -> bool:
    return ("is_guest" in st.session_state) and (st.session_state.is_guest)


def make_login_form(translator: LanguageTranslator) -> None:
    # Page login
    write_header(translator("welcome_not_logged"), subheader="")
    st.write("")
    _, col, _ = st.columns([1, 3, 1])
    col.button(
        translator("login_signup"),
        on_click=st.login,
        kwargs={"provider": "auth0"},
        use_container_width=True,
        type="primary",
    )
    st.write("")
    st.write("")
    write_subheader(translator("click_to_connect_as_guest"), bold=False)
    _, col, _ = st.columns([1, 3, 1])
    guest_button = col.button(
        translator("connect_as_guest"), use_container_width=True, type="secondary"
    )
    st.write("")
    st.write("")
    cont = st.container(border=True)
    cont.markdown(translator("padel_tracker_kezako"))
    if guest_button:
        st.session_state.is_guest = True
        st.rerun()


def make_finalize_signup_form(translator: LanguageTranslator) -> None:
    write_header(translator("finalize_signup"))

    # Case are you already a registered player ?
    form_existing = st.form("finalize_signup_existing_player")
    with form_existing:
        write_subheader(translator("finalize_signup_existing_player_message_header"))
        write_subheader(
            translator("finalize_signup_existing_player_message_sub"),
            bold=False,
            font_size=18,
        )
        with DB.get_session() as session:
            players_no_user = player_manager.get_all_players_without_user(session)
            players_name_no_user = [p.name for p in players_no_user]
        existing_player_name = st.selectbox(
            translator("existing_player"), options=players_name_no_user
        )
        # Submit button
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            submit_button_existing = st.form_submit_button(
                label=translator("submit"), use_container_width=True
            )
    ## Create if clicked
    if submit_button_existing:
        try:
            dict_auth_user = st.experimental_user.to_dict()
            dict_auth_user["name"] = existing_player_name
            dict_auth_user["nickname"] = existing_player_name
            with DB.get_session() as session:
                user = user_manager.create_user_from_auth_user(
                    session=session,
                    dict_auth_user=dict_auth_user,
                    default_language=st.session_state.language,
                    is_create_player=False,
                )
                # Fetch existing player and assign to user
                player = player_manager.get_player_from_name(
                    session=session, name=existing_player_name
                )
                user_manager.assign_player_to_user(
                    session=session, player=player, user=user
                )
            st.success(translator("user_added_success"), icon="🔥")
        except Exception as exc:
            st.error(f"{translator("user_added_error")}: {exc}", icon="💥")
        else:
            refresh_cache(only=ALL_CACHE_KEYS)
            st.rerun()

    # Case not registered
    form_not_existing = st.form("finalize_signup_not_existing_player")
    with form_not_existing:
        write_subheader(
            translator("finalize_signup_not_existing_player_message_header")
        )
        write_subheader(
            translator("finalize_signup_not_existing_player_message_sub"),
            bold=False,
            font_size=18,
        )
        # Name
        try:
            fetched_default_name = user_manager.determine_default_username(
                st.experimental_user.to_dict()
            )
        except Exception:
            fetched_default_name = ""
        username = st.text_input(
            translator("name"),
            value=fetched_default_name,
            help=translator("username_help"),
        )
        # Assign default league if wanted
        try:
            leagues = st.session_state.league_names
        except (AttributeError, KeyError):
            leagues = None
        existing_league_name = st.selectbox(
            translator("existing_league"),
            options=leagues,
            placeholder=translator("existing_league_message"),
            index=None,
            help=translator("existing_league_help"),
        )
        # Submit button
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            submit_button_not_existing = st.form_submit_button(
                label=translator("submit"), use_container_width=True
            )
    ## Create if clicked
    if submit_button_not_existing:
        try:
            dict_auth_user = st.experimental_user.to_dict()
            dict_auth_user["name"] = username
            dict_auth_user["nickname"] = username
            with DB.get_session() as session:
                user_manager.create_user_from_auth_user(
                    session=session,
                    dict_auth_user=dict_auth_user,
                    default_language=st.session_state.language,
                    is_create_player=True,
                    default_league_name=existing_league_name,
                )
                # Fetch freshly created player and assign to league
                if existing_league_name:
                    player = player_manager.get_player_from_name(
                        session=session, name=username
                    )
                    league = league_manager.get_league_from_name(
                        session=session, name=existing_league_name
                    )
                    league_manager.assign_league_to_player(
                        session=session, player=player, league=league
                    )
            st.success(translator("user_added_success"), icon="🔥")
        except InvalidPlayerNameError:
            st.error(f"{username}{translator("player_invalid_name_error")}", icon="💢")
        except Exception as exc:
            st.error(f"{translator("user_added_error")}: {exc}", icon="💥")
        else:
            refresh_cache(only=ALL_CACHE_KEYS)
            st.rerun()


def show_current_user_sidebar() -> None:
    """Show user.name / user.email if possible"""
    if "user" in st.session_state and st.session_state.user:
        try:
            name = st.session_state.user["name"]
            email = st.session_state.user["email"]
            if email:
                string = f"""
                    **{name}**      
                    ({email})
                """
            else:
                string = f"""
                    **{name}**      
                """
            st.sidebar.markdown(string)
        except Exception:
            pass


def perform_logout() -> None:
    st.session_state.user = None
    st.session_state.is_guest = False
    st.logout()


def display_sidebar_logout_button(translator: LanguageTranslator) -> None:
    st.sidebar.divider()
    show_current_user_sidebar()
    # Logout button
    st.sidebar.button(
        translator("logout"),
        on_click=perform_logout,
        type="secondary",
        icon="🚪",
        use_container_width=True,
    )
