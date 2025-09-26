import streamlit as st
import lib.load_data as ld
import matplotlib.pyplot as plt
import re

st.title("Starbench Dashboard")

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


# Show a streamlit diagram with all dataframes overlaid
st.write("### Overlay of all time series dataframes")
st.write(f"Loaded {len(data_frames)} data frames from `qmph/` folder with `_load.txt` suffix.")
st.write("QmpH data, larger is better - **Q**uery **m**ixes **p**er **H**our.")

# Plot all series on the same figure
fig, ax = plt.subplots(figsize=(14, 8))
for fname, df in data_frames.items():
    ax.plot(df['date'], df['value'], marker='o', linestyle='-', label=fname)

ax.set_xlabel('date')
ax.set_ylabel('value')
ax.set_title('Time Series Values for Each Benchmark')
ax.grid(True, alpha=0.3)
ax.legend(loc='best')
plt.tight_layout()
st.pyplot(fig)


# List of available dataframes
df_names = list(data_frames.keys())

st.write("### Overlay of all time series dataframes")

# Widget to select a dataframe
selected_name = st.selectbox("Select a source data-frame", df_names)
selected_df = data_frames[selected_name]

# Plot a specific time series
st.line_chart(selected_df['value'])


st.write("### Change-Point Analysis")

