import streamlit as st

from padel_tracker.ui.headers import write_header
from padel_tracker.ui.languages import DEFAULT_TRANSLATOR

st.write("")

if "translator" not in st.session_state:
    st.session_state.translator = DEFAULT_TRANSLATOR
translator = st.session_state.translator

if not st.experimental_user.is_logged_in:
    write_header(
        translator("welcome_not_logged"), subheader=translator("click_to_login")
    )
    st.button(
        translator("login_signup"), on_click=st.login, kwargs={"provider": "auth0"}
    )
    st.write("")
    # TODO (prio2): See as guest feature (correct redirect)
    guest_button = st.button(translator("connect_as_guest"))
    if guest_button:
        st.session_state.is_guest = True
        st.switch_page("streamlit_app.py")
