import streamlit as st

from padel_tracker.utils.conf import is_test_mode


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
