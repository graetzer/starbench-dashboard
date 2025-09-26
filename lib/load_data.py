import os
import pandas as pd
import re

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
                "value": float(parts[i]),
                "date_commit": date_commit
            })
        except ValueError:
            continue

    return results


def load_qmph_frames(folder="qmph", name_regex="*._load", limit_days=None):
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

            df = pd.DataFrame(all_data)
            df = df.sort_values('date_commit').reset_index(drop=True)
            df = df.groupby('date_commit')['value'].mean().reset_index()

            # Extract date from date_commit
            df['date'] = df['date_commit'].str.split('-').str[:3].str.join('-')
            df['date'] = pd.to_datetime(df['date'])

            df = df.set_index('date_commit')
            if limit_days is not None and len(df) > limit_days:
                df = df.iloc[-limit_days:]
            data_frames[test_name] = df
    return data_frames

# Example usage:
# dfs = load_qmph_frames(folder="qmph", name_regex=".*_load", limit_days=limit_days)
# print(dfs.keys())
# print(dfs['bsbm100m_load'].head())
