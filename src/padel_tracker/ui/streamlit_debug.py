"""
# My first app
Here's our first attempt at using data to create a table:
"""

from time import sleep

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from padel_tracker.utils.paths import get_absolute_path


LOGO_IMG = get_absolute_path(__file__, "./img/padel_logo.jpg")
st.logo(LOGO_IMG, size="large")

# TODO : use metrics
st.metric(label="Elo", value="1032", delta="-12")


# Layout
## Sidebar : Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?", ("Email", "Home phone", "Mobile phone")
)

## Columns inside a tab
left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.button("Press me!")
# Or even better, call Streamlit functions inside a "with" block:
with right_column:
    chosen = st.radio(
        "Sorting hat", ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin")
    )
    st.write(f"You are in {chosen} house!")


# For charts
df_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["a", "b", "c"],
)

st.write("Table")
st.write(df_data)

# st.write("Static table")
# st.table(df_data)

st.write("Line chart")
st.line_chart(df_data)

# st.header("Altair chart")
# chart_alt = alt.Chart(df_data).mark_point().encode(
#     x="a",
#     y="b",
# )
# st.altair_chart(chart_alt)

sleep(2)
st.toast("TOAAST", icon="😍")

st.sidebar.form_submit_button()