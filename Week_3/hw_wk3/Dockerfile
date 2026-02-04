# Use official Python image as base
FROM python:3.13-slim

# Set working directory inside the container
WORKDIR /app

# Copy uv binary from official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Install required Python packages using uv
RUN uv pip install --system \
    google-cloud-storage \
    pandas \
    pyarrow \
    requests

# Copy your Python script into the container (assume we're in Week_3/hw_wk3/)
COPY load_yellow_taxi_data.py .

# Copy your service account credentials
# (we'll mount this as a volume instead for better security)
# COPY gcs.json .

# Set the entrypoint to run the Python script
ENTRYPOINT ["python", "load_yellow_taxi_data.py"]