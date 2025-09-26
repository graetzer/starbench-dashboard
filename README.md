# Starbench Correlation Dashboard

This project analyzes and visualizes time series benchmark data from the `qmph/` folder. It provides interactive dashboards and correlation analysis using Streamlit and Jupyter notebooks.

## Features
- Load and parse multiple benchmark time series from tab-separated files
- Interactive dashboards with Streamlit
- Overlay and compare multiple benchmarks
- Pairwise and rolling correlation analysis
- Change-point detection
- Custom file selection via regex
- Docker deployment for easy sharing

## Quickstart
1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Run the Streamlit app:**
   ```sh
   streamlit run app.py
   ```
3. **Build and run with Docker:**
   ```sh
   docker build -t starbench-app .
   docker run -p 8501:8501 starbench-app
   ```

## Data Format
- Files in `qmph/` are tab-separated, with each line containing values, a date+commit string, and expected values.
- Example line:
  ```
  83.6\t2025-09-21-eda6f2d1d9-v12.0.0-SNAPSHOT-20250920\tExpected: 82.96\t
  ```

## Notebooks
- Main analysis notebook: `time_series_correlation.ipynb`
- See notebook for code examples and workflow.

## Development
- Python 3.11 recommended
- All dependencies listed in `requirements.txt`
- See `.gitignore` and `.dockerignore` for excluded files

