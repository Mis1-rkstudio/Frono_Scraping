from flask import Flask
import datetime
import pytz

from scripts.main import run_all_reports



app = Flask(__name__)

# Initialize last run time as None
last_run_time = None

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

@app.route("/", methods=["GET"])
def home():
    global last_run_time
    if last_run_time:
        ist_time = last_run_time.astimezone(IST)
        last_run = ist_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_run = "No runs yet"

    return f"""
    <h2>🛠️ Frono Automation Service</h2>
    <p>Welcome! This Cloud Run service powers the automated scraping, file processing, and BigQuery uploads for FronoCloud reports.</p>
    <ul>
        <li>✅ <a href="/status"><b>/status</b></a> → Health check endpoint </li>
        <li>🚀 <a href="/run"><b>/run</b></a> → Trigger scraping and data upload process </li>
    </ul>
    <hr>
    <p><b>🕒 Last Scraper Run (IST):</b> {last_run}</p>
    """, 200

@app.route("/status", methods=["GET"])
def health_check():
    return "✅ Service is healthy", 200

@app.route("/run", methods=["GET"])
def run_scraper():
    global last_run_time

    now = datetime.datetime.now(IST)
    current_hour = now.hour

    # Allow execution only between 11 AM and 9 PM IST
    if 11 <= current_hour < 21:
        last_run_time = datetime.datetime.now(pytz.utc)  # Save UTC time
        run_all_reports()
        return f"🚀 Scraper started at {now.strftime('%Y-%m-%d %H:%M:%S')} IST", 200
    else:
        return f"⏸️ Outside allowed time window (Current IST: {now.strftime('%H:%M:%S')}). Scraper not run.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
