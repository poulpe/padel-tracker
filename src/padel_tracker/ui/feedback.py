import requests
from typing import Any

import streamlit as st

from padel_tracker.ui.languages import LanguageTranslator
from padel_tracker.ui.headers import write_header, write_subheader

GITHUB_API_URL = "https://api.github.com/repos/poulpe/padel-tracker/issues"


def create_github_issue(title: str, body: str, github_token: str) -> tuple[bool, Any]:
    """Creates an issue directly on the Github repo of the project

    Parameters
    ----------
    title:str
        Title of the Github issue
    body:str
        Content
    github_token:str
        Typically #GITHUB_TOKEN = st.secrets["github"]["github_api_token"]

    Returns
    -------
    response_success:bool
        True if executed successfully, False otherwise
    response_body:Any
        as json
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"title": title, "body": body}
    response = requests.post(GITHUB_API_URL, headers=headers, json=data)
    return response.status_code == 201, response.json()


def set_session_state_is_feedback_clicked() -> None:
    st.session_state.is_feedback_clicked = True


def set_session_state_is_feedback_ongoing() -> None:
    st.session_state.is_feedback_ongoing = True


def make_feedback_button(translator: LanguageTranslator) -> bool:
    st.sidebar.divider()
    button = st.sidebar.button(
        translator("feedback_button"),
        type="tertiary",
        icon="🐞",
        use_container_width=True,
        on_click=set_session_state_is_feedback_clicked,
    )
    return button


def send_feedback(title: str, body: str, translator: LanguageTranslator):
    success, response = create_github_issue(
        title=title, body=body, github_token=st.secrets["github"]["github_api_token"]
    )
    if success:
        msg = f" {translator("feedback_submit_success")}: {response["html_url"]}"
        st.success(msg, icon="😘")
    else:
        st.error(f" {translator("feedback_submit_error")}: {response}", icon="💥")


def make_feedback_form(translator: LanguageTranslator):
    st.write("")
    write_header(translator("feedback_header"))
    write_subheader(
        translator("feedback_subheader_line1"), bold=False, extra_line=False
    )
    write_subheader(translator("feedback_subheader_line2"), bold=False)
    st.markdown(translator("feedback_subsubheader"))

    with st.form("feedback"):
        title = st.text_input(translator("feedback_title"))
        body = st.text_area(translator("feedback_description"))
        st.form_submit_button(
            translator("submit"), on_click=set_session_state_is_feedback_ongoing
        )

    st.session_state.is_feedback_ongoing = False
    if title != "" and body != "":
        send_feedback(title, body, translator)
