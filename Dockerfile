FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
 wget \
 unzip \
 gnupg \
 curl \
 fonts-liberation \
 libappindicator3-1 \
 libasound2 \
 libatk-bridge2.0-0 \
 libatk1.0-0 \
 libcups2 \
 libdbus-1-3 \
 libgdk-pixbuf2.0-0 \
 libnspr4 \
 libnss3 \
 libx11-xcb1 \
 libxcomposite1 \
 libxdamage1 \
 libxrandr2 \
 xdg-utils \
 libu2f-udev \
 libvulkan1 \
 libxss1 \
 libglib2.0-0 \
 libdrm2 \
 libgbm1 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && apt install -y ./google-chrome.deb \
 && rm google-chrome.deb

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
 DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | grep -A1 $CHROME_VERSION | grep "url" | head -1 | cut -d '"' -f 4) && \
 wget -q -O chromedriver.zip $DRIVER_VERSION && \
 unzip chromedriver.zip -d /usr/local/bin && \
 rm chromedriver.zip

# Set environment variables for Chrome headless
ENV CHROME_BIN="/usr/bin/google-chrome" \
 CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"

# Set working directory
WORKDIR /app
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Run using Gunicorn
# CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
CMD ["python", "app.py"]
