import base64
from pathlib import Path

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from padel_tracker.ui.login import make_login_form, make_finalize_signup_form

st.set_page_config(page_title="Padel Tracker", page_icon="🥎")

from padel_tracker.utils.errors import UserNotFoundError
from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.models.users import UserRole
from padel_tracker.database.db import DB
from padel_tracker.services import user_manager
from padel_tracker.ui.languages import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    LanguageTranslator,
)
from padel_tracker.ui.cache import update_cache, refresh_cache, CacheKey
from padel_tracker.ui.cards import define_cards_css
from padel_tracker.ui.headers import write_subheader
from padel_tracker.ui.threads import get_thread_pool
from padel_tracker.main import init_app

##### Init #####
if ("is_app_init" not in st.session_state) or (not st.session_state.is_app_init):
    init_app(threaded_logs=True, thread_pool=get_thread_pool())
    st.session_state.is_app_init = True


##### Image utils func #####
@st.cache_data  # image_path as str to make it 100% hashable safe
def get_base64_image(image_path_str: str) -> str:
    image_path = Path(image_path_str)
    with image_path.open("rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded


LOGO_IMG = get_absolute_path(__file__, "./img/padel_logo.jpg")
LOGO_IMG_BASE64 = get_base64_image(str(LOGO_IMG))

##### Translation feature in Session state
if "language" not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE
    st.session_state.translator = LanguageTranslator(DEFAULT_LANGUAGE)

translator = st.session_state.translator

##### Start app def and top header #####
st.logo(LOGO_IMG, size="large")
html_code_top_header = f"""
<div style="text-align: center;">
    <img src="data:image/jpeg;base64,{LOGO_IMG_BASE64}" alt="Padel Logo" style="max-width: 20%;">
    <div style="font-size: 40px; font-weight: bold; margin: 0;"> Padel Tracker </div>
</div>
"""
st.markdown(html_code_top_header, unsafe_allow_html=True)

##### Fetch user if logged_in #####
if st.experimental_user.is_logged_in:
    if ("user" not in st.session_state) or (st.session_state.user is None):
        auth_user_id = st.experimental_user["sub"]
        with DB.get_session() as session:
            try:
                user = user_manager.get_user_from_auth_user_id(
                    session=session, auth_user_id=auth_user_id
                )
                st.session_state.user = user.model_dump()
            except UserNotFoundError:
                # Means new user, will be redirected to "finalize_signup"
                st.session_state.user = None

is_guest = ("is_guest" in st.session_state) and (st.session_state.is_guest)

##### Sidebar ######
# Make selectable league in sidebar
update_cache(only=CacheKey.df_leagues, force=True)
if "league_name" not in st.session_state:
    # Try fetching default league from user
    user_league = None
    if ("user" in st.session_state) and (st.session_state.user):
        user_league = st.session_state.user["default_league_name"]
    # Determine default league
    if user_league:
        st.session_state.league_name = user_league
    else:
        try:
            st.session_state.league_name = st.session_state.league_names[0]
        except (KeyError, TypeError):
            # st.warning(translator("no_league_database_error"), icon="💢")
            # TODO (prio3): fallback display page_add_league (because pg.run() won't run)
            st.stop()

if st.experimental_user.is_logged_in or is_guest:
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
def update_session_state_translator() -> None:
    st.session_state.translator = LanguageTranslator(st.session_state.language)


st.sidebar.selectbox(
    st.session_state.translator("language"),
    SUPPORTED_LANGUAGES,
    key="language",
    index=SUPPORTED_LANGUAGES.index(st.session_state.language),
    on_change=update_session_state_translator,
)


# Logout button
def perform_logout():
    st.session_state.user = None
    st.session_state.is_guest = False
    st.logout()
    st.rerun()


if (st.experimental_user.is_logged_in) or is_guest:
    st.sidebar.divider()
    st.sidebar.button(
        translator("logout"),
        on_click=perform_logout,
        type="secondary",
        icon="🚪",
        use_container_width=True,
    )

##### Define CSS #####
define_cards_css()

##### Determine if execution on computer or mobile #####
if ("screen_inner_width" not in st.session_state) or (
    st.session_state.screen_inner_width is None
):
    screen_inner_width = streamlit_js_eval(
        js_expressions="window.innerWidth", key="WIDTH", want_output=True
    )
    device_type = "pc"  # Default
    if screen_inner_width is not None:
        device_type = "mobile" if screen_inner_width < 550 else "pc"
        st.session_state.screen_inner_width = screen_inner_width
    st.session_state.device_type = device_type

##### Fetch most used data from database and store in cache #####
update_cache()

##### Pages definition #####
## Standard pages
page_overview = st.Page("page_overview.py", title="Overview", icon="🥎", default=True)
page_add_match = st.Page("page_add_match.py", title=translator("add_match"), icon="➕")
page_check_player = st.Page(
    "page_check_player.py",
    title=translator("check_player"),
    icon="👤",
)
page_check_team = st.Page(
    "page_check_team.py",
    title=translator("check_team"),
    icon="🤝",
)
page_manage_account = st.Page(
    "page_manage_account.py",
    title=translator("manage_account"),
    icon="⚙️",
)
## Admin pages
page_add_player = st.Page(
    "page_add_player.py", title=translator("add_player"), icon="🆕"
)
page_delete_player = st.Page(
    "page_delete_player.py",
    title=translator("delete_player"),
    icon="🙅",
)
page_delete_match = st.Page(
    "page_delete_match.py", title=translator("delete_match"), icon="❌"
)
page_add_league = st.Page(
    "page_add_league.py", title=translator("add_league"), icon="🏆"
)
page_assign_league = st.Page(
    "page_assign_league.py",
    title=translator("assign_league"),
    icon="👥️",
)
page_check_logs = st.Page(
    "page_check_logs.py", title=translator("check_logs"), icon="📋"
)

# Define pages dict
pages_guest = {
    "Padel Tracker": [page_overview],
    translator("players_teams"): [page_check_player, page_check_team],
}
pages_player = {
    "Padel Tracker": [page_overview],
    translator("matches"): [page_add_match],
    translator("players_teams"): [page_check_player, page_check_team],
    translator("my_account"): [page_manage_account],
}
pages_admin = {
    "Padel Tracker": [page_overview],
    translator("matches"): [page_add_match],
    translator("players_teams"): [page_check_player, page_check_team],
    # TODO (prio 3): translator("leagues"): [page_check_leagues],
    translator("my_account"): [page_manage_account],
    translator("administration"): [
        page_add_player,
        page_delete_player,
        page_delete_match,
        page_add_league,
        page_assign_league,
        page_check_logs,
    ],
}

# Determine pages to show based on user
is_guest = ("is_guest" in st.session_state) and (st.session_state.is_guest)
is_user_not_defined = (
    ("user" not in st.session_state)
    or (st.session_state.user is None)
    or (st.session_state.user["player_id"] is None)
)
is_finalize_signup = (not is_guest) and is_user_not_defined
if not st.experimental_user.is_logged_in and not is_guest:
    make_login_form(translator=translator)
elif is_finalize_signup:
    # Case logged but no user linked
    make_finalize_signup_form(translator=translator)
else:
    if is_guest:
        # Case "see as guest"
        pages = pages_guest
    # Case logged in as Player OK
    elif st.session_state.user["role"] == UserRole.PLAYER:
        pages = pages_player
    # Case logged in as Admin OK
    elif st.session_state.user["role"] == UserRole.ADMIN:
        pages = pages_admin
    else:
        st.error(translator("unknown_pages_error"), icon="💥")
        raise KeyError("unknown situation to generate pages")
    pg = st.navigation(pages=pages)
    pg.run()
