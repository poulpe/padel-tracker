import base64
from pathlib import Path

import streamlit as st

from padel_tracker.utils.paths import get_absolute_path


@st.cache_data  # image_path as str to make it 100% hashable safe
def get_base64_image(image_path_str: str) -> str:
    image_path = Path(image_path_str)
    with image_path.open("rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded


LOGO_IMG = get_absolute_path(__file__, "./img/padel_logo.jpg")
LOGO_IMG_BASE64 = get_base64_image(str(LOGO_IMG))


@st.cache_data
def get_html_logo_header() -> str:
    return f"""
    <div style="text-align: center;">
        <img src="data:image/jpeg;base64,{LOGO_IMG_BASE64}" alt="Padel Logo" style="max-width: 20%;">
        <div style="font-size: 40px; font-weight: bold; margin: 0;"> Padel Tracker </div>
    </div>
    """


def display_logo_and_top_header():
    st.logo(LOGO_IMG, size="large")
    st.markdown(get_html_logo_header(), unsafe_allow_html=True)
