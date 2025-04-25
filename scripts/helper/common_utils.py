import os
import time
from google.cloud import bigquery
import pandas as pd


def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def wait_for_download(directory, extension=".xlsx", timeout=30):
    log("Waiting for download to complete...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = [f for f in os.listdir(directory) if f.endswith(extension) and not f.endswith(".crdownload")]
        if files:
            return os.path.join(directory, files[0])
        time.sleep(1)
    raise Exception("Download timeout")

def ensure_download_path(folder_name):
    path = os.path.join(os.getcwd(), "Kolkata", folder_name)
    os.makedirs(path, exist_ok=True)
    return path

def load_credentials():
    username = os.environ.get("FRONO_USERNAME")
    password = os.environ.get("FRONO_PASSWORD")
    if not username or not password:
        raise EnvironmentError("FRONO_USERNAME or FRONO_PASSWORD is missing.")
    return username, password

def upload_to_bigquery(file_path, table_name, dataset_id="frono_2025"):
    """
    Uploads Excel data to BigQuery. 
    If the dataset doesn't exist, it will be automatically created.

    Args:
        file_path (str): Local path to the Excel file.
        table_name (str): Table name to create or append data to.
        dataset_id (str): Dataset ID in BigQuery (defaults to 'frono_2025').
        overwrite (bool): If True, overwrites the existing table.
    """
    client = bigquery.Client()
    df = pd.read_excel(file_path)
    project_id = client.project
    table_id = f"{project_id}.{dataset_id}.{table_name}"

    # Check if dataset exists
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    try:
        client.get_dataset(dataset_ref)  # Will succeed if dataset exists
        log(f"📦 Dataset exists: {dataset_id}")
    except Exception as e:
        # Dataset does not exist, so create it
        log(f"📦 Dataset not found: {dataset_id}. Creating new dataset...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "asia-south1"  # You can change location if needed
        client.create_dataset(dataset)
        log(f"✅ Created dataset: {dataset_id}")

    # Set upload configuration
    write_mode = bigquery.WriteDisposition.WRITE_TRUNCATE  # or WRITE_APPEND
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_mode,
        autodetect=True
    )

    # Upload data
    log(f"📤 Uploading {df.shape[0]} rows to table: {table_id}")
    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        log(f"✅ Upload complete: {table_id}")
    except Exception as e:
        log(f"❌ Failed to upload to {table_id}: {e}")
        raise
