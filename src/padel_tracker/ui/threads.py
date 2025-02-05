from concurrent.futures.thread import ThreadPoolExecutor

import streamlit as st


@st.cache_resource
def get_thread_pool():
    return ThreadPoolExecutor(max_workers=8)


THREAD_POOL = get_thread_pool()
