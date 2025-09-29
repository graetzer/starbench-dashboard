import os
import pandas as pd
import re
import stardog
import streamlit as st

# Valid QMPH line formats include one or more float values followed by a date_commit string and an "Expected:" section.
# Examples:
# 58586.667	89091.771	111560.313	129307.053	2025-09-21-eda6f2d1d9-v12.0.0-SNAPSHOT-20250920	Expected: 53770.9	72647.2	105003	122430	
# 126.8	2025-09-21-eda6f2d1d9-v12.0.0-SNAPSHOT-20250920	Expected: 108.74	
def extract_line_parts(line): 
    start = line.find('\tExpected: ')
    if start == -1:
        return None
    line = line[:start].strip()
    parts = line.split('\t')
    if len(parts) < 2:
        return None
    return parts

def parse_qmph_line(line):
    parts = extract_line_parts(line)
    if parts is None or len(parts) < 2:
        return []
    
    date_commit = parts[-1]
    results = list()

    for i in range(len(parts)-1):
        try:
            results.append({
                "qmph": float(parts[i]),
                "date_commit": date_commit
            })
        except ValueError:
            continue

    return results

def convert_qmph_to_data_frame(all_data):
    df = pd.DataFrame(all_data)
    df = df.sort_values('date_commit').reset_index(drop=True)
    df = df.groupby('date_commit')['qmph'].mean().reset_index()

    # Extract date from date_commit
    df['date'] = df['date_commit'].str.split('-').str[:3].str.join('-')
    df['date'] = pd.to_datetime(df['date'])
    df['commit'] = df['date_commit'].str.split('-').str[3]

    df = df.set_index('date_commit')
    return df

folder = "qmph"
def load_qmph_frames(name_regex=".*_load", limit_days=None):
    """
    Load all time series data frames from the specified folder using a file_predicate function.
    Returns a dictionary of DataFrames indexed by benchmark name.
    Optionally filters to the last N days if limit_days is set.
    """
    data_frames = dict()
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        test_name = fname[:-4]
        if not re.fullmatch(name_regex, test_name):
            continue

        with open(path, "r") as f:
            all_data = []
            for line in f:
                all_data.extend(parse_qmph_line(line))

            df = convert_qmph_to_data_frame(all_data)
            if limit_days is not None and len(df) > limit_days:
                df = df.iloc[-limit_days:]
            data_frames[test_name] = df

    return data_frames

# Example usage:
# dfs = load_qmph_frames(folder="qmph", name_regex=".*_load", limit_days=limit_days)
# print(dfs.keys())
# print(dfs['bsbm100m_load'].head())

dashboard_db = "sb-dashboard"
with open("lib/list_all_tests.sparql", 'r') as f:
    sparql_query_fetch_all_tests = f.read()

with open("lib/fetch_qmph_data.sparql", 'r') as f:
    sparql_query_fetch_test_data = f.read()

def convert_sb_dashboard_to_data_frame(all_data):
    df = pd.DataFrame(all_data)
    df = df.sort_values(['build', 'date']).reset_index(drop=True)
    #df = df.groupby('date')['value'].mean().reset_index()
    df['date'] = pd.to_datetime(df['date'])

    # make a compund index of build, date and commit
    df['build_date'] = df['build'] + '-' + df['date'].dt.strftime('%Y-%m-%d') + '-' + df['commit']
    df = df.set_index('build_date')
    return df

def load_sd_dashboard_test(conn, test_name, testiri, limit_days=None):
    query = sparql_query_fetch_test_data.replace('?num_days', str(limit_days))
    results = conn.select(query, bindings={'testIri': f"<{testiri}>"})
    time_series = dict()

    for binding in results['results']['bindings']:
        # Process each binding as needed
        client = binding['clients']['value']
        value = float(binding['actual']['value'])
        date = binding['date']['value']
        if time_series.get(client) is None:
            time_series[client] = list()

        time_series[client].append({
            "date": date,
            "commit": binding['commit']['value'],
            "build": binding['build']['value'],
            "qmph": value
        })

    data_frames = dict()
    if len(time_series) == 1:
        # If there's only one client, we can simplify the structure
        client_data = time_series.popitem()[1]
        data_frames[test_name] = convert_sb_dashboard_to_data_frame(client_data)
    else:
        # If there are multiple clients, create one series each
        for client, data in time_series.items():
            data_frames[f"{test_name}_{client}"] = convert_sb_dashboard_to_data_frame(data)

    return data_frames


def load_sb_dashboard_data(name_regex=".*_load", limit_days=None, credentials=None):
    data_frames = dict()
    # verify limit_days is an integer
    if limit_days is not None and (not isinstance(limit_days, int) or limit_days <= 0):
        raise ValueError("limit_days must be a positive integer or None")
    if limit_days is None:
        limit_days = 100  # default to 100 days if not specified

    # Use provided credentials
    if not isinstance(credentials, dict):
        raise ValueError("Credentials must be provided for Stardog connection")

    with stardog.Connection(dashboard_db, **credentials) as conn:
        results = conn.select(sparql_query_fetch_all_tests)
        for row in results['results']['bindings']:
            test_name = row['test']['value']
            testiri = row['testIri']['value']
            if re.fullmatch(name_regex, test_name):
                matching_df = load_sd_dashboard_test(conn, test_name, testiri, limit_days)
                data_frames.update(matching_df)

    return data_frames

# Streamlit-cached function for loading data frames
@st.cache_data(show_spinner=True)
def cached_load_sb_dashboard_data(conn_creds, name_regex, limit_days):
    # Use the supplied login credentials from session_state
    return load_sb_dashboard_data(name_regex=name_regex, limit_days=limit_days, credentials=conn_creds)

def load_data_frames(name_regex, limit_days):
    if 'login' not in st.session_state or not isinstance(st.session_state.login, dict):
        st.warning("Offline mode. Showing local `qmph/` data only.")
        data_frames = load_qmph_frames(name_regex=name_regex, limit_days=limit_days)
        st.write(f"Loaded {len(data_frames)} data frames from `qmph/` folder with `_load.txt` suffix.")
    else:
        # Use the supplied login credentials from session_state
        data_frames = cached_load_sb_dashboard_data(conn_creds=st.session_state.login, name_regex=name_regex, limit_days=limit_days)
        st.write(f"Loaded {len(data_frames)} data frames from {dashboard_db} on {st.session_state.login['endpoint']}.")
    return data_frames