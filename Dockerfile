# Start from an official lightweight Python image
FROM python:3.11-slim

# 🛠 Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-driver \
    chromium \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    wget \
    unzip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 🛠 Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/bin/chromedriver

# 📂 Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📂 Copy project files
COPY . .

# 🌐 Expose port 8080
EXPOSE 8080

# 🚀 Start the app
CMD ["python", "main.py"]
