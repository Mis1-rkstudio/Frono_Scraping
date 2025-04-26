FROM python:3.10-slim

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y \
    wget curl unzip xvfb libxi6 libgconf-2-4 libnss3 libxss1 libasound2 libgbm1 libgtk-3-0 \
    chromium chromium-driver fonts-liberation && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver
ENV DISPLAY=:99

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app
WORKDIR /app

# Run the app
CMD ["python", "main.py"]
