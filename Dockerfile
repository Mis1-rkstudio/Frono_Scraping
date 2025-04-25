# Use lightweight Python base image
FROM python:3.10-slim

# Install system dependencies for Chrome + Selenium
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libgbm1 \
    libxss1 \
    chromium \
    chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Set working directory to /app
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire codebase including scripts and .env
COPY . .

# Set PYTHONPATH to recognize helper modules inside scripts/
ENV PYTHONPATH=/app/scripts

# Run the main script
CMD ["python", "main.py"]
