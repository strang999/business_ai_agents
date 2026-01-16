# Docker Deployment for Warehouse Forecasting

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY config.py ./
COPY state.py ./

# Create directories
RUN mkdir -p data/Test\ data output

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Volume for data (NDA protected)
VOLUME ["/app/data"]

# Volume for output
VOLUME ["/app/output"]

# Default command
CMD ["python", "main.py", "--horizon", "30"]
