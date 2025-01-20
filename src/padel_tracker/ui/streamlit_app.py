import base64
from pathlib import Path

import streamlit as st

from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.ui.languages import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    LanguageTranslator,
)
from padel_tracker.ui.cards import define_cards_css
from padel_tracker.main import init_app

##### Init #####
init_app()
st.set_page_config(page_title="Padel Tracker", page_icon="🥎")


##### Utils func #####
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


def update_session_state_translator() -> None:
    st.session_state.translator = LanguageTranslator(st.session_state.language)


st.sidebar.selectbox(
    st.session_state.translator("language"),
    SUPPORTED_LANGUAGES,
    key="language",
    index=SUPPORTED_LANGUAGES.index(st.session_state.language),
    on_change=update_session_state_translator,
)

##### Start app def and top header #####
st.logo(LOGO_IMG, size="large")
custom_sub_header = "Ligue des Pédales du Padel"

html_code_top_header = f"""
<div style="text-align: center;">
    <img src="data:image/jpeg;base64,{LOGO_IMG_BASE64}" alt="Padel Logo" style="max-width: 20%;">
    <div style="font-size: 40px; font-weight: bold; margin: 0;"> Padel Tracker </div>
    <div style="font-size: 16px; margin: 0;"> {custom_sub_header} </div>
</div>
"""
st.markdown(html_code_top_header, unsafe_allow_html=True)

##### Define CSS #####
define_cards_css()

##### Pages definition #####
page_overview = st.Page("page_overview.py", title="Overview", icon="🗺️", default=True)
page_add_match = st.Page(
    "page_add_match.py", title=st.session_state.translator("add_match"), icon="➕"
)
page_players = st.Page(
    "page_players.py", title=st.session_state.translator("players_teams"), icon="👥️"
)

pg = st.navigation(
    {
        "Padel Tracker": [page_overview],
        st.session_state.translator("matches"): [page_add_match],
        st.session_state.translator("players_teams"): [page_players],
        st.session_state.translator("analytics"): [],
    }
)

pg.run()
