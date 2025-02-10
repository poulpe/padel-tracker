import streamlit as st

from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager, user_manager
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.languages import LanguageTranslator
from padel_tracker.ui.cache import refresh_cache


def make_login_form(translator: LanguageTranslator) -> None:
    # Page login
    write_header(
        translator("welcome_not_logged"), subheader=translator("click_to_login")
    )
    # TODO (prio3) : welcome message to explain PadelTracker + instructions
    _, col, _ = st.columns([1, 3, 1])
    col.button(
        translator("login_signup"),
        on_click=st.login,
        kwargs={"provider": "auth0"},
        use_container_width=True,
        type="primary",
    )
    st.write("")
    guest_button = col.button(
        translator("connect_as_guest"), use_container_width=True, type="secondary"
    )
    if guest_button:
        st.session_state.is_guest = True
        st.rerun()


def make_finalize_signup_form(translator: LanguageTranslator) -> None:
    # Case are you already a registered player ?
    form_existing = st.form("finalize_signup_existing_player")
    with form_existing:
        write_subheader(translator("finalize_signup_existing_player_message"))
        with DB.get_session() as session:
            players_no_user = player_manager.get_all_players_without_user(session)
            players_name_no_user = [p.name for p in players_no_user]
        cont = st.container(border=True)
        with cont:
            write_subheader(translator("finalize_signup_assign_player"))
            existing_player_name = st.selectbox(
                translator("existing_player"), options=players_name_no_user
            )
        # Submit button
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            submit_button_existing = st.form_submit_button(
                label=translator("submit"), use_container_width=True
            )

    # Case not registered
    form_not_existing = st.form("finalize_signup_not_existing_player")
    with form_not_existing:
        write_subheader(translator("finalize_signup_not_existing_player_message"))
        # Name
        try:
            fetched_default_name = user_manager.determine_default_username(
                st.experimental_user.to_dict()
            )
        except Exception:
            fetched_default_name = ""
        username = st.text_input(translator("name"), value=fetched_default_name)
        # Assign default league if wanted
        existing_league_name = st.selectbox(
            translator("existing_league"),
            options=st.session_state.league_names,
            placeholder=translator("existing_league_message"),
            index=None,
        )
        # Submit button
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            submit_button_not_existing = st.form_submit_button(
                label=translator("submit"), use_container_width=True
            )

    # Create if clicked
    if submit_button_existing:
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
        refresh_cache()
        st.rerun()

    if submit_button_not_existing:
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
        refresh_cache()
        st.rerun()
