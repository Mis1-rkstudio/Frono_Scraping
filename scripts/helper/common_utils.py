import os
import time
# from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd

# load_dotenv()

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
    username = os.environ.get("FRONO_USERNAME")           # For Production
    password = os.environ.get("FRONO_PASSWORD")           # For Production
    # username = os.getenv("FRONO_USERNAME")                  # For Development
    # password = os.getenv("FRONO_PASSWORD")                  # For Development
    if not username or not password:
        raise EnvironmentError("FRONO_USERNAME or FRONO_PASSWORD is missing.")
    return username, password


def load_dataframe(file_path):
    print(f"📂 Loading file: {file_path}")

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        raise ValueError("Unsupported file type. Only .csv and .xlsx are supported.")

    return df

def upload_to_bigquery(df, table_name, dataset_id="frono_2025", overwrite=True):
    """
    Loads a local file using `load_dataframe` and uploads it to BigQuery.
    Creates the dataset if it doesn't exist.

    Args:
        file_path (str): Full local path to the Excel or CSV file.
        table_name (str): Target BigQuery table name.
        dataset_id (str): BigQuery dataset name (default: 'frono_2025').
        overwrite (bool): If True, overwrites the existing table.
    """
    client = bigquery.Client()
    project_id = client.project
    table_id = f"{project_id}.{dataset_id}.{table_name}"

    # Ensure dataset exists
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    try:
        client.get_dataset(dataset_ref)
        log(f"📦 Dataset exists: {dataset_id}")
    except Exception as e:
        log(f"📦 Dataset not found: {dataset_id}. Creating...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "asia-south1"
        client.create_dataset(dataset)
        log(f"✅ Created dataset: {dataset_id}")

    # Upload configuration
    write_mode = bigquery.WriteDisposition.WRITE_TRUNCATE
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_mode,
        autodetect=True
    )

    # Upload
    log(f"📤 Uploading {df.shape[0]} rows to table: {table_id}")
    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        log(f"✅ Upload complete: {table_id}")
    except Exception as e:
        log(f"❌ Failed to upload to {table_id}: {e}")
        raise

