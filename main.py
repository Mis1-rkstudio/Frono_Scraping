from flask import Flask
import threading
import datetime
import pytz
import scripts.main as scraper  # Your scraping function


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
        <li>✅ <b>/health</b> → Health check endpoint</li>
        <li>🚀 <b>/run</b> → Trigger scraping and data upload process</li>
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
    last_run_time = datetime.datetime.now(pytz.utc)  # Save time in UTC first
    threading.Thread(target=scraper.run_all_reports).start()
    return "🚀 Scraper started!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
