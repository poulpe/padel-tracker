from dataclasses import dataclass

import streamlit as st
from streamlit.navigation.page import StreamlitPage

from padel_tracker.ui.languages import LanguageTranslator


@dataclass
class PagesCollection:
    GUEST: dict[str, list[StreamlitPage]] = None
    PLAYER: dict[str, list[StreamlitPage]] = None
    TRUSTEDPLAYER: dict[str, list[StreamlitPage]] = None
    ADMIN: dict[str, list[StreamlitPage]] = None

    def make_pages(self, translator: LanguageTranslator) -> None:
        ## Standard pages
        page_overview = st.Page(
            "page_overview.py", title="Overview", icon="🥎", default=True
        )
        page_add_match = st.Page(
            "page_add_match.py",
            title=translator("add_match"),
            url_path="add_match",
            icon="➕",
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
        page_join_league = st.Page(
            "page_join_league.py",
            title=translator("join_league"),
            url_path="join_league",
            icon="👥️",
        )
        # page_manage_account = st.Page(
        #     "page_manage_account.py",
        #     title=translator("manage_account"),
        #     url_path="manage_account",
        #     icon="⚙️",
        # )
        ## League pages
        page_manage_league = st.Page(
            "page_manage_league.py",
            title=translator("manage_my_league"),
            url_path="manage_league",
            icon="🏆",
        )
        page_add_player_in_league = st.Page(
            "page_add_player_in_league.py",
            title=translator("add_player"),
            url_path="add_player_in_league",
            icon="🆕",
        )
        page_add_league = st.Page(
            "page_add_league.py",
            title=translator("add_league"),
            url_path="add_league",
            icon="📋",
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
        page_check_logs = st.Page(
            "page_check_logs.py",
            title=translator("check_logs"),
            url_path="check_logs",
            icon="📜",
        )
        page_assign_league = st.Page(
            "page_assign_league.py",
            title=translator("assign_league"),
            url_path="assign_league",
            icon="🔗",
        )
        ## About pages
        page_about = st.Page(
            "page_about.py",
            title=translator("about"),
            url_path="about",
            icon="ℹ️",
        )
        page_feedback = st.Page(
            "page_feedback.py",
            title=translator("feedback_button"),
            url_path="feedback",
            icon="🐞",
        )
        # Define pages dict
        self.GUEST = {
            "Padel Tracker": [page_overview],
            translator("players_teams"): [page_check_player, page_check_team],
            translator("about_and_feedback"): [page_about, page_feedback],
        }
        self.PLAYER = {
            "Padel Tracker": [page_overview],
            translator("matches"): [page_add_match],
            translator("players_teams"): [page_check_player, page_check_team],
            translator("league"): [
                page_manage_league,
                page_add_player_in_league,
                page_add_league,
            ],
            translator("my_account"): [page_join_league],  # , page_manage_account],
            translator("about_and_feedback"): [page_about, page_feedback],
        }
        self.TRUSTEDPLAYER = {
            "Padel Tracker": [page_overview],
            translator("matches"): [page_add_match],
            translator("players_teams"): [page_check_player, page_check_team],
            translator("league"): [
                page_manage_league,
                page_add_player_in_league,
                page_add_league,
            ],
            translator("my_account"): [page_join_league],  # , page_manage_account],
            translator("about_and_feedback"): [page_about, page_feedback],
        }
        self.ADMIN = {
            "Padel Tracker": [page_overview],
            translator("matches"): [page_add_match],
            translator("players_teams"): [page_check_player, page_check_team],
            translator("league"): [
                page_manage_league,
                page_add_player_in_league,
                page_add_league,
            ],
            translator("my_account"): [page_join_league],  # , page_manage_account],
            translator("administration"): [
                page_check_logs,
                page_delete_match,
                page_add_player,
                page_assign_league,
                page_delete_player,
            ],
            translator("about_and_feedback"): [page_about, page_feedback],
        }
