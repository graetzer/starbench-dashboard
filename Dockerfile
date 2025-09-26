# Basic Dockerfile for Streamlit app deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# For most Streamlit apps, build-essential is not strictly necessary unless your Python dependencies require compilation (e.g., some scientific libraries).
# If your requirements.txt only includes pandas, numpy, matplotlib, and streamlit, you can safely omit build-essential.
# If you encounter installation errors for packages needing compilation, add it back.

# Example: No build-essential (minimal)
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose default Streamlit port
EXPOSE 8501

# Start the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
