import streamlit as st

from padel_tracker.utils.conf import is_test_mode
from padel_tracker.ui.languages import LanguageTranslator


def determine_is_logged_in() -> bool:
    if not is_test_mode():
        return ("is_logged_in" in st.user) and st.user.is_logged_in
    else:
        return (
            ("user" in st.session_state)
            and st.session_state.user
            and ("is_logged_in" in st.session_state.user)
            and st.session_state.user["is_logged_in"]
        )


def display_add_player_in_league_button(translator: LanguageTranslator) -> None:
    st.info(translator("add_player_in_league_info"), icon="↘️")
    _, col_center, _ = st.columns([1, 5, 1])
    with col_center:
        button_add_player = st.button(
            translator("add_player"), type="primary", use_container_width=True
        )
    if button_add_player:
        st.switch_page("page_add_player_in_league.py")


def display_add_league_button(translator: LanguageTranslator) -> None:
    _, col_center, _ = st.columns([1, 5, 1])
    with col_center:
        button_add_league = st.button(
            translator("add_league"), type="primary", use_container_width=True
        )
    if button_add_league:
        st.switch_page("page_add_league.py")


def display_no_default_league_warning(translator: LanguageTranslator) -> None:
    """Display warning message + help button"""
    st.info(translator("user_without_default_league_message"), icon="⚠️")
    display_add_league_button(translator)
