# Copilot Instructions for starbench-correlation

## Project Overview
This project analyzes time series correlations for benchmark data, primarily using Jupyter notebooks and raw text files. Data is stored in the `qmph/` folder as tab-separated files, and analysis is performed in `time_series_correlation.ipynb`.

There is also a Streamlit app (`app.py`) for visualizing the time series data interactively.

## Data Architecture
- **Raw Data**: Located in `qmph/`, each file contains lines like:
  `83.6\t2025-09-21-eda6f2d1d9-v12.0.0-SNAPSHOT-20250920\tExpected: 82.96\t`
- **Parsing Pattern**: Extract value, date+commit hash, and expected value from each line. See notebook code for parsing logic.
- **Notebook Analysis**: Main workflow is in `time_series_correlation.ipynb`, which loads, cleans, visualizes, and correlates time series data.

## Developer Workflow
- **Data Loading**: Use the `load_qmph_frames` function to specify which files from `qmph/` to analyze.
- **Parsing**: Follow the notebook's example for splitting lines and extracting fields. Use pandas DataFrames for further analysis.
- **Visualization**: Matplotlib is used for plotting; seaborn is optional but commented out.
- **Correlation**: Merge DataFrames on date, then use pandas `.corr()` or numpy/scipy for correlation metrics.

## Conventions & Patterns
- **File Naming**: Data files in `qmph/` are named by benchmark/test type (e.g., `bsbm_rm1rm.txt`).
- **Notebook Structure**: Each analysis step is a separate cell, with markdown for documentation and code for execution.
- **DataFrame Columns**: Always convert values to float and dates to pandas datetime for consistency.
- **Duplicates**: Handle duplicate dates by averaging values (see commented code in notebook).

## Integration Points
- **External Dependencies**: pandas, numpy, matplotlib (see first notebook cell for imports).
- **No build/test scripts**: Analysis is interactive via Jupyter; no automated build or test pipeline detected.

## Example: Parsing a Data File
```python
parts = line.strip().split('\t')
value = float(parts[0])
date_commit = parts[1].split('-')
date = '-'.join(date_commit[:3])
commit_hash = date_commit[3] if len(date_commit) > 3 else None
expected = float(parts[2].replace('Expected: ', '').strip())
```

## Key Files & Directories
- `qmph/`: Raw data files
- `time_series_correlation.ipynb`: Main analysis notebook

---
If any section is unclear or missing, please provide feedback or specify which workflow/component needs more detail.