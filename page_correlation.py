import streamlit as st
import load_data as ld
import pandas as pd
import re

st.title("Starbench Test Correlation")

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

# Prepare a dictionary of DataFrames indexed by benchmark name
series_dict = {name: df['value'] for name, df in data_frames.items()}

# Align all series on their date_commit index
all_series = [s for s in series_dict.values()]
common_index = all_series[0].index
for s in all_series[1:]:
    common_index = common_index.intersection(s.index)

# Reindex all series to the common dates
aligned_series = {name: s.loc[common_index] for name, s in series_dict.items()}

# Build a DataFrame for correlation calculation
corr_df = pd.DataFrame(aligned_series)

# Calculate pairwise correlations
corr_matrix = corr_df.corr()
st.write("Pairwise Pearson Correlation Table:")

st.dataframe(corr_matrix.style.format("{:.2f}"))

# Other types of analysis:
# - Rolling correlation (see pandas.rolling)
# - Cross-correlation (lag analysis)
# - Granger causality (statsmodels)
# - Cointegration (statsmodels)
# - Clustering time series (scikit-learn)
# - Change point detection (ruptures)
# - Visualization: heatmaps, pairplots
# - Outlier detection
# - Seasonal decomposition (statsmodels)

st.write("### Rolling Correlation")
st.write("Select two tests to compute and visualize their rolling correlation over time.")

# Widget to select two dataframes for rolling correlation
df_names = list(data_frames.keys())
col1, col2 = st.columns(2)
with col1:
    selected_name1 = st.selectbox("First Test", df_names, index=0)
with col2:
    selected_name2 = st.selectbox("Second Test", df_names, index=1 if len(df_names) > 1 else 0)

selected_df1 = aligned_series[selected_name1]
selected_df2 = aligned_series[selected_name2]

# Compute rolling correlation
window_size = st.slider("Rolling window size (in data points)", min_value=2, max_value=days_default, value=7)
rolling_corr = selected_df1.rolling(window=window_size).corr(selected_df2)
st.line_chart(rolling_corr, height=400)
