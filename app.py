import os
import shutil
from flask import Flask

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
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Report Runner API</title>
        <style>
            body {
                background-color: #f9f9f9;
                font-family: 'Segoe UI', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
            }
            h2 {
                margin-bottom: 10px;
                color: #2f855a;
            }
            p {
                margin-top: 0;
                margin-bottom: 20px;
                color: #666;
            }
            .btn-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 250px;
                margin: 0 auto;
            }
            .btn {
                background-color: #2f855a;
                color: white;
                border: none;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                transition: background-color 0.2s ease;
            }
            .btn:hover {
                background-color: #276749;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>✅ Report Runner API</h2>
            <p>Select a task to trigger:</p>
            <div class="btn-container">
                <a class="btn" href="/status">Check Status</a>
                <a class="btn" href="/daily">Run Daily Reports</a>
                <a class="btn" href="/every2days">Run Every 2 Days</a>
                <a class="btn" href="/every4h">Run Every 4 Hours</a>
                <a class="btn" href="/every2h">Run Every 2 Hours</a>
                <a class="btn" href="/cleanup">Cleanup Folders</a>
            </div>
        </div>
    </body>
    </html>
    '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
