# Base image with Python
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
 wget \
 unzip \
 gnupg \
 curl \
 ca-certificates \
 fonts-liberation \
 libnss3 \
 libatk-bridge2.0-0 \
 libxss1 \
 libasound2 \
 libgbm-dev \
 libgtk-3-0 \
 libx11-xcb1 \
 libxcomposite1 \
 libxdamage1 \
 libxrandr2 \
 libu2f-udev \
 xdg-utils \
 && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-keyring.gpg && \
 echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
 apt-get update && apt-get install -y google-chrome-stable && \
 rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
 wget -q https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
 unzip chromedriver_linux64.zip && \
 mv chromedriver /usr/local/bin/chromedriver && \
 chmod +x /usr/local/bin/chromedriver && \
 rm chromedriver_linux64.zip

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH=$PATH:/usr/local/bin/chromedriver

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app
WORKDIR /app

# Run your main script
CMD ["python", "app.py"]
