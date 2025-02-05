import base64
from concurrent.futures.thread import ThreadPoolExecutor

# import sys  # TODO: st.stop() instead of sys.exit() ?
from pathlib import Path

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.ui.languages import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    LanguageTranslator,
)
from padel_tracker.ui.cache import update_cache, CacheKey
from padel_tracker.ui.cards import define_cards_css
from padel_tracker.ui.headers import write_subheader
from padel_tracker.main import init_app

##### Init #####
st.set_page_config(page_title="Padel Tracker", page_icon="🥎")
if "thread_pool" not in st.session_state:
    st.session_state.thread_pool = ThreadPoolExecutor(max_workers=5)
if ("is_app_init" not in st.session_state) or (not st.session_state.is_app_init):
    init_app(thread_pool=st.session_state.thread_pool)
    st.session_state.is_app_init = True


##### Image utils func #####
@st.cache_data
def get_base64_image(image_path: Path) -> str:
    with image_path.open("rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded


LOGO_IMG = get_absolute_path(__file__, "./img/padel_logo.jpg")
LOGO_IMG_BASE64 = get_base64_image(LOGO_IMG)

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

##### Sidebar ######
# Make selectable league in sidebar
update_cache(only=CacheKey.df_leagues, force=True)
if "league_name" not in st.session_state:
    try:
        st.session_state.league_name = st.session_state.league_names[0]
    except (KeyError, TypeError):
        # Warning already st.warning(translator("no_league_database_error"), icon="💢")
        # TODO (prio3): fallback display page_add_league (because pg.run() won't run)
        st.stop()
st.sidebar.selectbox(
    translator("league"),
    st.session_state.league_names,
    key="league_name",
    on_change=update_cache,
    kwargs={"force": True},
)
write_subheader(
    st.session_state.league_name, font_size=21, bold=False, extra_line=False
)
# st.sidebar.divider()


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

# TODO: user features (+ see as guest = no show add/edit pages), so different navigations dict based on context

pg = st.navigation(
    {
        "Padel Tracker": [page_overview],
        translator("matches"): [page_add_match],
        translator("players_teams"): [page_check_player, page_check_team],
        # TODO: translator("leagues"): [page_check_leagues],
        # translator("analytics"): [],
        translator("administration"): [
            page_add_player,
            page_delete_player,
            page_delete_match,
            page_add_league,
            page_assign_league,
            page_check_logs,
        ],
    }
)
pg.run()
