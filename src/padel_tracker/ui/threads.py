import threading
from concurrent.futures.thread import ThreadPoolExecutor

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx


@st.cache_resource
def get_thread_pool():
    return ThreadPoolExecutor(max_workers=16)


def run_thread_with_st(fn, *args, **kwargs):
    """Exécute une fonction dans un thread avec le contexte Streamlit attaché."""
    ctx = get_script_run_ctx()  # Récupère le contexte actuel de Streamlit

    def wrapper():
        fn(*args, **kwargs)  # Exécute la fonction

    # Créer un thread et attacher le contexte
    thread = threading.Thread(target=wrapper)
    if ctx:
        add_script_run_ctx(thread, ctx)  # Attache le contexte Streamlit au thread
    thread.start()
