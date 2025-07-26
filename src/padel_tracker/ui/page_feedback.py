import streamlit as st

from padel_tracker.ui.languages import get_translator
from padel_tracker.ui.headers import write_header, write_subheader
from padel_tracker.ui.feedback import create_github_issue

translator = get_translator()

st.write("")
write_header(translator("feedback_header"))
write_subheader(translator("feedback_subheader_line1"), bold=False, extra_line=False)
write_subheader(translator("feedback_subheader_line2"), bold=False)
st.markdown(translator("feedback_subsubheader"))

with st.form("feedback"):
    title = st.text_input(translator("feedback_title"))
    body = st.text_area(translator("feedback_description"))
    submit_button = st.form_submit_button(translator("submit"))

if submit_button:
    if (not title) or (not body):
        st.error(translator("feedback_inputs_error"), icon="💢")
        st.stop()

    success, response = create_github_issue(
        title=title, body=body, github_token=st.secrets["github"]["github_api_token"]
    )
    if success:
        msg = f"  {translator("feedback_submit_success")}: {response["html_url"]}"
        st.success(msg, icon="😘")
    else:
        st.error(f"  {translator("feedback_submit_error")}: {response}", icon="💥")
