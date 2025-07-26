import streamlit as st

st.set_page_config(page_title="Padel Tracker", page_icon="🥎")

from padel_tracker.models.users import UserRole
from padel_tracker.ui.cards import define_cards_css
from padel_tracker.ui.headers import write_subheader
from padel_tracker.ui.threads import get_thread_pool
from padel_tracker.ui.images import display_logo_and_top_header
from padel_tracker.ui.pages import PagesCollection
from padel_tracker.ui.cache import (
    update_cache,
    refresh_cache,
    CacheKey,
    determine_session_state_device_type,
    determine_session_state_league_name,
)
from padel_tracker.ui.languages import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    LanguageTranslator,
    update_session_state_translator,
)
from padel_tracker.ui.login import (
    make_login_form,
    make_finalize_signup_form,
    determine_is_guest,
    determine_is_logged_in,
    display_sidebar_logout_button,
    log_user_visit,
)
from padel_tracker.main import init_app

##### Init #####
if ("is_app_init" not in st.session_state) or (not st.session_state.is_app_init):
    init_app(threaded_logs=True, thread_pool=get_thread_pool())
    st.session_state.is_app_init = True

##### Translation feature in Session state
if "language" not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE
    st.session_state.translator = LanguageTranslator(DEFAULT_LANGUAGE)

translator = st.session_state.translator

##### Start app def and top header #####
display_logo_and_top_header()

##### Fetch user if logged_in #####
is_logged_in = determine_is_logged_in()
if is_logged_in:
    if ("user" not in st.session_state) or (st.session_state.user is None):
        update_cache(only=CacheKey.user, force=True)
        log_user_visit()

is_guest = determine_is_guest()

##### Sidebar ######
# Make selectable league in sidebar
update_cache(only=CacheKey.df_leagues, force=False)
determine_session_state_league_name()

if is_logged_in or is_guest:
    st.sidebar.selectbox(
        translator("league"),
        st.session_state.league_names,
        key="league_name",
        on_change=refresh_cache,
    )
    write_subheader(
        st.session_state.league_name, font_size=21, bold=False, extra_line=False
    )

# Language selector in sidebar
st.sidebar.selectbox(
    st.session_state.translator("language"),
    SUPPORTED_LANGUAGES,
    key="language",
    index=SUPPORTED_LANGUAGES.index(st.session_state.language),
    on_change=update_session_state_translator,
)

# Logout button
if is_logged_in or is_guest:
    display_sidebar_logout_button(translator)

##### Define CSS #####
define_cards_css()

##### Determine if execution on computer or mobile #####
determine_session_state_device_type()

##### Fetch most used data from database and store in cache #####
update_cache()

##### Pages definition #####
# Determine conditions based on user
is_undefined_user = (
    ("user" not in st.session_state)
    or (st.session_state.user is None)
    or (st.session_state.user["player_id"] is None)
)
is_finalize_signup = (not is_guest) and is_undefined_user

# Define pages and run navigation
pages = PagesCollection()
pages.make_pages(translator=translator)

if not is_logged_in and not is_guest:
    make_login_form(translator=translator)
elif is_finalize_signup:
    make_finalize_signup_form(translator=translator)  # = logged but no user linked
else:
    if is_guest:
        current_pages = pages.GUEST
    elif st.session_state.user["role"] == UserRole.PLAYER:
        current_pages = pages.PLAYER
    elif st.session_state.user["role"] == UserRole.TRUSTEDPLAYER:
        current_pages = pages.TRUSTEDPLAYER
    elif st.session_state.user["role"] == UserRole.ADMIN:
        current_pages = pages.ADMIN
    else:
        st.error(translator("unknown_pages_error"), icon="💥")
        raise KeyError("unknown situation to generate pages") from None
    pg = st.navigation(pages=current_pages)
    pg.run()
