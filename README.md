# Frono CloudRun Automation

## Overview

This project automates the scraping, processing, and uploading of business reports from FronoCloud for multiple locations (Kolkata, Surat). It leverages Selenium for web automation, pandas for data processing, and Google BigQuery for cloud storage. The automation is orchestrated via a Flask web service, designed to run on Google Cloud Run, and is fully containerized with Docker.

## Features

- Automated scraping of various business reports from FronoCloud
- Data cleaning and transformation using pandas
- Upload of processed data to Google BigQuery
- Scheduled and on-demand runs via Flask endpoints
- Modular scripts for each report type and location
- Headless browser automation with Selenium
- Google Sheets integration for item management

## Directory Structure

```
frono-cloudrun-automation_optimised/
├── app.py                  # Flask app and scheduler entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Containerization setup
├── service_account_key.json# Google Cloud service account (DO NOT COMMIT REAL KEYS)
├── scripts/                # Main automation scripts
│   ├── main.py             # Orchestrates all report scripts
│   ├── account_payable.py  # Scrapes Account Payable report
│   ├── ...                 # Other report scripts
│   ├── add_new_item.py     # Google Sheets-driven item addition
│   ├── helper/             # Browser, login, and utility helpers
│   └── df_cleaners/        # DataFrame cleaning utilities
├── kolkata/                # Output folders for Kolkata reports
├── surat/                  # Output folders for Surat reports
```

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd frono-cloudrun-automation_optimised
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment variables:**

   - Set FronoCloud credentials for each location (e.g., `FRONO_KOLKATA_USERNAME`, `FRONO_KOLKATA_PASSWORD`, etc.)
   - Set Google Cloud credentials: either set `GOOGLE_APPLICATION_CREDENTIALS` or place `service_account_key.json` in the root directory.
   - (Optional) Set `ITEMS_SPREADSHEET_ID` for Google Sheets integration.

4. **Local run:**
   ```bash
   python app.py
   ```

## Usage

- **Web endpoints:**
  - `/` : Home/info page
  - `/status` : Health check
  - `/run` : Trigger scraping and upload (allowed 12 PM–9 PM IST)
- **Scheduler:**
  - Runs every 2 hours between 12 PM and 9 PM IST (Asia/Kolkata)

## Deployment (Docker & Cloud Run)

1. **Build Docker image:**
   ```bash
   docker build -t frono-cloudrun-automation .
   ```
2. **Run locally:**
   ```bash
   docker run -p 8080:8080 --env-file .env frono-cloudrun-automation
   ```
3. **Deploy to Google Cloud Run:**
   - Push image to Google Container Registry
   - Deploy via Cloud Console or `gcloud run deploy`

## Security Notes

- **Never commit real service account keys to public repos.**
- Use environment variables for all secrets and credentials.
- Restrict service account permissions to the minimum required.

## Contributing

Pull requests and issues are welcome! Please ensure code is well-documented and tested.

## License

[MIT](LICENSE) (or specify your license)
