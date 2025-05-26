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


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app
WORKDIR /app

# Run your main script
CMD ["python", "app.py"]
