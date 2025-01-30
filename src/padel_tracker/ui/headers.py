import streamlit as st

FONT_SIZE_HEADER = 30
FONT_SIZE_SUBHEADER = 20


def write_header(
    header: str,
    subheader: str = None,
    bold_subheader: bool = False,
    font_size_header: int = FONT_SIZE_HEADER,
    font_size_subheader: int = FONT_SIZE_SUBHEADER,
) -> None:
    """Writes centered text to streamlit, header/title like, but centered"""
    text = f"""
        <div style="text-align: center;">
            <div style="font-size: {font_size_header}px; font-weight: bold; margin: 0;"> {header} </div>
        """
    if subheader:
        text += f'<div style="font-size: {font_size_subheader}px;'
        if bold_subheader:
            text += "font-weight: bold;"
        text += f'margin: 0;"> {subheader} </div>'
    text += "<br></div>"
    st.markdown(text, unsafe_allow_html=True)


def write_subheader(
    subheader: str, font_size: int = FONT_SIZE_SUBHEADER, bold: bool = True
) -> None:
    """Writes centered text to streamlit, subheader/subtitle like, but centered"""
    text = f"""
        <div style="text-align: center;">
            <div style="font-size: {font_size}px; 
    """
    if bold:
        text += "font-weight: bold; "
    text += f'margin: 0;"> {subheader} </div> <br></div>'
    st.markdown(text, unsafe_allow_html=True)
