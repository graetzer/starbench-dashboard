import streamlit as st
import lib.load_data as ld
import streamlit as st
import matplotlib.pyplot as plt

st.title("Starbench Dashboard")

col1, col2 = st.columns(2)
with col1:
    # Add a slider to control the number of days to load
    # Use st.sidebar.slider(...) to place the slider in the sidebar
    limit_days = st.slider("Limit to last N days", min_value=1, max_value=360, value=90)
with col2:
    # Textbox for user to input for a custom wildcard regex
    name_regex_input = st.text_input("Test Matching Predicate (regex)", value="bsbm100m.*_barq")

# Show a streamlit diagram with all dataframes overlaid
st.write("### Overlay of all time series dataframes")

# Checks session data for login property
# and loads data either from Stardog or local qmph/ folder
data_frames = ld.load_data_frames(name_regex=name_regex_input, limit_days=limit_days)

st.write("QmpH data, larger is better - **Q**uery **m**ixes **p**er **H**our.")

# Plot all series on the same figure
fig, ax = plt.subplots(figsize=(14, 8))
for fname, df in data_frames.items():
    ax.plot(df['date'], df['qmph'], marker='o', linestyle='-', label=fname)

ax.set_xlabel('date')
ax.set_ylabel('QmpH')
ax.set_title('Time Series QmpH Values for Each Benchmark')
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
st.line_chart(selected_df['qmph'])
