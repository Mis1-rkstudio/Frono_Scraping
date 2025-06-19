import os
import time
import datetime 
import pandas as pd
from google.cloud import bigquery



# 🌍 Try loading .env if available (for local development)
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file.")

# 🔐 Local JSON auth (only if GOOGLE_APPLICATION_CREDENTIALS not already set)
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    if os.path.exists("service_account_key.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account_key.json"
        print("✅ Set GOOGLE_APPLICATION_CREDENTIALS for local run.")

        
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

def ensure_download_path(location, folder_name):
    path = os.path.join(os.getcwd(), location, folder_name)
    os.makedirs(path, exist_ok=True)
    return path

def load_credentials(location="kolkata"):
    username = os.environ.get(f"FRONO_{location.upper()}_USERNAME")
    password = os.environ.get(f"FRONO_{location.upper()}_PASSWORD")
    if not username or not password:
        raise EnvironmentError(f"Missing credentials for {location}")
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




def infer_bigquery_schema(df, custom_schema_map=None):
    """Generate a BigQuery schema from a DataFrame with optional overrides."""
    schema = []
    for col in df.columns:
        if custom_schema_map and col in custom_schema_map:
            # Use explicitly provided type
            bq_type = custom_schema_map[col]
        else:
            # Infer automatically from pandas dtype
            dtype = df[col].dtype
            if pd.api.types.is_integer_dtype(dtype):
                bq_type = "INT64"
            elif pd.api.types.is_float_dtype(dtype):
                bq_type = "FLOAT64"
            elif pd.api.types.is_bool_dtype(dtype):
                bq_type = "BOOL"
            elif pd.api.types.is_object_dtype(dtype) and df[col].apply(lambda x: isinstance(x, (pd.Timestamp, datetime.date))).any():
                bq_type = "DATE"
            else:
                bq_type = "STRING"
        schema.append(bigquery.SchemaField(col, bq_type))
    return schema



# def upload_to_bigquery(df, table_name, dataset_id="frono_2025", location="kolkata"):
#     log(f"Creating BigQuery client...")
#     client = bigquery.Client()
#     project_id = client.project

#     # ✅ Add prefix to table name
#     prefixed_table_name = f"{location.lower()}_{table_name}"
#     table_id = f"{project_id}.{dataset_id}.{prefixed_table_name}"


#     dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
#     try:
#         client.get_dataset(dataset_ref)
#         log(f"📦 Dataset exists: {dataset_id}")
#     except Exception:
#         log(f"📦 Dataset not found: {dataset_id}. Creating...")
#         dataset = bigquery.Dataset(dataset_ref)
#         dataset.location = "asia-south1"
#         client.create_dataset(dataset)
#         log(f"✅ Created dataset: {dataset_id}")

#     write_mode = bigquery.WriteDisposition.WRITE_TRUNCATE
#     job_config = bigquery.LoadJobConfig(
#         write_disposition=write_mode,
#         autodetect=True
#     )

#     log(f"📤 Uploading {df.shape[0]} rows to table: {table_id}")
#     job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
#     job.result()
#     log(f"✅ Upload complete: {table_id}")

# def upload_to_bigquery(df, table_name, dataset_id="frono_2025", location="kolkata"):
#     log(f"Creating BigQuery client...")
#     client = bigquery.Client()
#     project_id = client.project

#     # ✅ Add prefix to table name
#     prefixed_table_name = f"{location.lower()}_{table_name}"
#     table_id = f"{project_id}.{dataset_id}.{prefixed_table_name}"

#     # ✅ Preprocess date columns
#     for col in df.columns:
#         if col.lower() in ['date', 'dates', 'datetime', 'timestamp']:
#             try:
#                 df[col] = pd.to_datetime(df[col])
#             except Exception as e:
#                 log(f"Warning: Could not convert {col} to datetime: {str(e)}")

#     # ✅ Ensure dataset exists
#     dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
#     try:
#         client.get_dataset(dataset_ref)
#         log(f"📦 Dataset exists: {dataset_id}")
#     except Exception:
#         log(f"📦 Dataset not found: {dataset_id}. Creating...")
#         dataset = bigquery.Dataset(dataset_ref)
#         dataset.location = "asia-south1"
#         client.create_dataset(dataset)
#         log(f"✅ Created dataset: {dataset_id}")

#     # ✅ Configure upload with schema
#     job_config = bigquery.LoadJobConfig(
#         write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)

#     # ✅ Upload to BigQuery
#     log(f"📤 Uploading {df.shape[0]} rows to table: {table_id}")
#     job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
#     job.result()
#     log(f"✅ Upload complete: {table_id}")

def upload_to_bigquery(df, table_name, dataset_id="frono_2025", location="kolkata", custom_schema_map=None):
    log(f"Creating BigQuery client...")
    client = bigquery.Client()
    project_id = client.project

    prefixed_table_name = f"{location.lower()}_{table_name}"
    table_id = f"{project_id}.{dataset_id}.{prefixed_table_name}"

    # ✅ Convert columns marked as DATE in custom_schema_map only
    if custom_schema_map:
        for col, col_type in custom_schema_map.items():
            if col_type == "DATE" and col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
                    log(f"🗓️ Converted column '{col}' to date (via custom_schema_map)")
                except Exception as e:
                    log(f"⚠️ Could not convert {col} to date: {str(e)}")


    # ✅ Get schema from helper
    schema = infer_bigquery_schema(df, custom_schema_map)

    # ✅ Ensure dataset exists
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    try:
        client.get_dataset(dataset_ref)
        log(f"📦 Dataset exists: {dataset_id}")
    except Exception:
        log(f"📦 Dataset not found: {dataset_id}. Creating...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "asia-south1"
        client.create_dataset(dataset)
        log(f"✅ Created dataset: {dataset_id}")

    # Upload with custom schema
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=schema
    )

    log(f"📤 Uploading {df.shape[0]} rows to table: {table_id}")
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    log(f"✅ Upload complete: {table_id}")

