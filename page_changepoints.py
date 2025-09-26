import streamlit as st
import load_data as ld
import pandas as pd
import ruptures as rpt
import matplotlib.pyplot as plt
import re

st.title("Change Point Detection")

col1, col2 = st.columns(2)
with col1:
    # Add a slider to control the number of days to load
    # Use st.sidebar.slider(...) to place the slider in the sidebar
    limit_days = st.slider("Limit to last N days", min_value=1, max_value=360, value=180)
with col2:
    # Textbox for user to input for a custom wildcard regex
    file_predicate_input = st.text_input("File predicate (regex)", value=".*_load\.txt")

def filter_files_function(filename):
    return re.fullmatch(file_predicate_input, filename) is not None

# Load all time series dataframes with limit_days
data_frames = ld.load_qmph_frames(folder="qmph", file_predicate=filter_files_function, limit_days=limit_days)

if len(data_frames) < 2:
    st.write("Not enough data frames to compute correlations. Please ensure at least two `_load.txt` files are present in the `qmph` folder.")
    st.stop()
    exit()

# Prepare a dictionary of DataFrames indexed by benchmark name
series_dict = {name: df['value'] for name, df in data_frames.items()}

# Align all series on their date_commit index
all_series = [s for s in series_dict.values()]
common_index = all_series[0].index
for s in all_series[1:]:
    common_index = common_index.intersection(s.index)

# Reindex all series to the common dates
aligned_series = {name: s.loc[common_index] for name, s in series_dict.items()}

# Slider for ruptures penalty value
penalty_value = st.slider("Ruptures Penalty Value", min_value=1, max_value=100, value=10)

found_cps = 0
for name, series in aligned_series.items():
    values = series.values
    algo = rpt.Pelt(model="rbf").fit(values)
    # You can adjust the penalty value for sensitivity
    result = algo.predict(pen=penalty_value)
    # result contains indices where change points occur (end of segment)
    change_dates = series.index[result[:-1]]  # exclude last index (end of series)
    if change_dates.empty:
        #st.write(f"No change points detected for {name}.")
        continue

    found_cps += 1
    st.write(f"**Change points for {name}:**")

    for idx, date in zip(result[:-1], change_dates):
        st.write(f"Date & Commit: {date}")

    # Plot the resulting matplotlib figure
    fig, ax = rpt.display(values, result)
    fig.gca().set_title(f"Change Point Detection for {name}")
    st.pyplot(fig)

if found_cps == 0:
    st.write("No change points detected in any series.")