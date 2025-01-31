import streamlit as st


def make_player_selectbox(player_name: str = None):
    index = None
    if player_name:
        try:
            index = st.session_state.player_names.index(player_name)
        except ValueError:
            index = None
    player_name = st.selectbox(
        label=st.session_state.translator("player_name"),
        options=st.session_state.player_names,
        placeholder=st.session_state.translator("player"),
        index=index,
    )
    return player_name
