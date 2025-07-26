import streamlit as st

from padel_tracker.ui.languages import get_translator
from padel_tracker.ui.headers import write_header

translator = get_translator()

st.write("")
write_header(translator("about"))
cont = st.container(border=True)
cont.markdown(translator("padel_tracker_kezako"))

# TODO (prio 2): create section to explain Elo calculations, rankings...
