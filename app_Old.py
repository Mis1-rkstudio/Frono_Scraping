from flask import Flask
import datetime
import pytz
from scripts.main import (
    run_once_a_day_reports,
    run_once_in_2_days_reports,
    run_every_4_hours_reports,
    run_every_2_hours_reports,
)

app = Flask(__name__)

# Track last run time for display
last_run_time = None
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
        <li>🕐 <a href="/run_once_a_day"><b>/run_once_a_day</b></a> → Trigger once-a-day reports</li>
        <li>🗓️ <a href="/run_once_in_2_days"><b>/run_once_in_2_days</b></a> → Trigger once-in-2-days reports</li>
        <li>⏰ <a href="/run_every_4_hours"><b>/run_every_4_hours</b></a> → Trigger every-4-hours reports</li>
        <li>⏲️ <a href="/run_every_2_hours"><b>/run_every_2_hours</b></a> → Trigger every-2-hours reports</li>
    </ul>
    <hr>
    <p><b>🕒 Last Scraper Run (IST):</b> {last_run}</p>
    """, 200

@app.route("/status", methods=["GET"])
def health_check():
    return "✅ Service is healthy", 200


@app.route("/run_once_a_day", methods=["GET"])
def run_once_a_day_endpoint():
    global last_run_time
    last_run_time = datetime.datetime.now(pytz.utc)
    for location in ["kolkata", "surat"]:
        run_once_a_day_reports(location)
    return "✅ Triggered once a day reports", 200

@app.route("/run_once_in_2_days", methods=["GET"])
def run_once_in_2_days_endpoint():
    global last_run_time
    last_run_time = datetime.datetime.now(pytz.utc)
    for location in ["kolkata", "surat"]:
        run_once_in_2_days_reports(location)
    return "✅ Triggered once in 2 days reports", 200

@app.route("/run_every_4_hours", methods=["GET"])
def run_every_4_hours_endpoint():
    global last_run_time
    last_run_time = datetime.datetime.now(pytz.utc)
    for location in ["kolkata", "surat"]:
        run_every_4_hours_reports(location)
    return "✅ Triggered every 4 hours reports", 200

@app.route("/run_every_2_hours", methods=["GET"])
def run_every_2_hours_endpoint():
    global last_run_time
    last_run_time = datetime.datetime.now(pytz.utc)
    for location in ["kolkata", "surat"]:
        run_every_2_hours_reports(location)
    return "✅ Triggered every 2 hours reports", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
