import streamlit as st

from padel_tracker.ui.languages import LanguageTranslator, DEFAULT_LANGUAGE

if "language" not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE
    st.session_state.translator = LanguageTranslator(DEFAULT_LANGUAGE)

translator = st.session_state.translator

## Standard pages
page_overview = st.Page("page_overview.py", title="Overview", icon="🥎", default=True)
page_add_match = st.Page(
    "page_add_match.py", title=translator("add_match"), url_path="add_match", icon="➕"
)
page_check_player = st.Page(
    "page_check_player.py",
    title=translator("check_player"),
    url_path="check_player",
    icon="👤",
)
page_check_team = st.Page(
    "page_check_team.py",
    title=translator("check_team"),
    url_path="check_team",
    icon="🤝",
)
page_manage_account = st.Page(
    "page_manage_account.py",
    title=translator("manage_account"),
    url_path="manage_account",
    icon="⚙️",
)
## Admin pages
page_add_player = st.Page(
    "page_add_player.py",
    title=translator("add_player"),
    url_path="add_player",
    icon="🆕",
)
page_delete_player = st.Page(
    "page_delete_player.py",
    title=translator("delete_player"),
    url_path="delete_player",
    icon="🙅",
)
page_delete_match = st.Page(
    "page_delete_match.py",
    title=translator("delete_match"),
    url_path="delete_match",
    icon="❌",
)
page_add_league = st.Page(
    "page_add_league.py",
    title=translator("add_league"),
    url_path="add_league",
    icon="🏆",
)
page_assign_league = st.Page(
    "page_assign_league.py",
    title=translator("assign_league"),
    url_path="assign_league",
    icon="👥️",
)
page_check_logs = st.Page(
    "page_check_logs.py",
    title=translator("check_logs"),
    url_path="check_logs",
    icon="📋",
)

# Define pages dict
PAGES_GUEST = {
    "Padel Tracker": [page_overview],
    translator("players_teams"): [page_check_player, page_check_team],
}
PAGES_PLAYER = {
    "Padel Tracker": [page_overview],
    translator("matches"): [page_add_match],
    translator("players_teams"): [page_check_player, page_check_team],
    translator("my_account"): [page_manage_account],
    translator("administration"): [
        page_add_league,
        page_add_player,
        page_assign_league,
    ],
}
PAGES_ADMIN = {
    "Padel Tracker": [page_overview],
    translator("matches"): [page_add_match],
    translator("players_teams"): [page_check_player, page_check_team],
    # TODO (prio 3): translator("leagues"): [page_check_leagues],
    translator("my_account"): [page_manage_account],
    translator("administration"): [
        page_add_league,
        page_add_player,
        page_assign_league,
        page_delete_player,
        page_delete_match,
        page_check_logs,
    ],
}
