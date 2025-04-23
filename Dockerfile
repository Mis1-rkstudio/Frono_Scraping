FROM python:alpine

RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg chromium-driver chromium \
    fonts-liberation libnss3 libxss1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 && apt-get clean

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
