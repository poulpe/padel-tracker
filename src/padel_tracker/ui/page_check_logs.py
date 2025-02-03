import streamlit as st

from padel_tracker.models.base import Logs
from padel_tracker.database.db import DB, read_from_db
from padel_tracker.ui.headers import write_header

st.write("")

write_header(st.session_state.translator("check_logs"))

with DB.get_session() as session:
    df_logs = read_from_db(Logs, as_df=True, order_by=Logs.timestamp, order_descending=True)

col = ["timestamp", "name", "level", "message"]
st.dataframe(df_logs[col], use_container_width=True, hide_index=True, height=700)
