import os
import shutil
from flask import Flask, request

from scripts.main import run_every_2_hours_reports, run_every_4_hours_reports, run_once_a_day_reports, run_once_in_2_days_reports


app = Flask(__name__)

locations = ["kolkata", "surat"]



# Create HTTP endpoints
@app.route("/daily", methods=["GET","POST"])
def daily():
    for loc in locations:
        run_once_a_day_reports(loc)
    return "✅ Daily reports executed", 200

@app.route("/every2days", methods=["GET","POST"])
def every2days():
    for loc in locations:
        run_once_in_2_days_reports(loc)
    return "✅ Every 2 days reports executed", 200

@app.route("/every4h", methods=["GET","POST"])
def every4h():
    for loc in locations:
        run_every_4_hours_reports(loc)
    return "✅ Every 4 hours reports executed", 200

@app.route("/every2h", methods=["GET","POST"])
def every2h():
    for loc in locations:
        run_every_2_hours_reports(loc)
    return "✅ Every 2 hours reports executed", 200


@app.route("/status", methods=["GET"])
def health_check():
    return "✅ Service is healthy", 200

# DELETE kolkata and surat folders if they exist
@app.route("/cleanup", methods=["GET","POST"])
def cleanup_folders():
    deleted = []
    for folder in ["kolkata", "surat"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            deleted.append(folder)
    return f"✅ Deleted folders: {', '.join(deleted) if deleted else 'None'}", 200

@app.route("/", methods=["GET"])
def index():
    return "✅ Report Runner API is live."

if __name__ == "__main__":
    app.run(debug=True)
