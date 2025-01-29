import streamlit as st

from padel_tracker.ui.languages import DEFAULT_TRANSLATOR
from padel_tracker.ui.headers import write_header, write_subheader

# from padel_tracker.database.db import DB
from padel_tracker.ui.charts import make_player_metric_history_chart

st.write("")

if "translator" not in st.session_state.keys():
    st.session_state.translator = DEFAULT_TRANSLATOR

write_header(st.session_state.translator("check_player"))

# Make player selectbox
player_name = st.selectbox(
    label=st.session_state.translator("player_name"),
    options=st.session_state.player_names,
    placeholder=st.session_state.translator("player"),
)
st.write("")

# Graph
write_subheader(st.session_state.translator("evolution"))
make_player_metric_history_chart(
    player_name=player_name, translator=st.session_state.translator
)

# TODO: Short table (elo, rank, nb match, v, d, v/d) OR cool card ?

# TODO: All matches history cards + elo rating gain as metric ?

# TODO: Best teammate (player with the most common wins)

# TODO: Most frequent teammate (player with the most matches)

# TODO: Best rival or Black Beast (player against lost the most)

# TODO: Favorite victim (player against win the most
# (PLAYER_NAME
# X victoires contre lui/elle)
