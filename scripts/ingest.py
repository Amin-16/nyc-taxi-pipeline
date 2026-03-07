import requests
import os
import tempfile
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import storage

DTYPES = {
    "VendorID": "Int64",
    "RatecodeID": "Int64",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "passenger_count": "Int64",
    "payment_type": "Int64",
    "trip_type": "Int64",
    "store_and_fwd_flag": "str",
    "trip_distance": "float64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "ehail_fee": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
}

DATE_COLS = {
    "yellow": ["tpep_pickup_datetime", "tpep_dropoff_datetime"],
    "green": ["lpep_pickup_datetime", "lpep_dropoff_datetime"],
}

def blob_exists(bucket, blob_path: str) -> bool:
    return bucket.blob(blob_path).exists()

def download_and_upload(taxi_type: str, year: int, month: int, bucket_name: str):
    """
    Download parquet from TLC, enforce schema, upload clean parquet to GCS.
    This function will be called directly by Airflow task.
    """
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    blob_path = f"raw/{taxi_type}/{year}/{filename}"

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    if blob_exists(bucket, blob_path):
        print(f"⏭️  Skipping {filename} — already exists in GCS\n")
        return

    print(f"⬇️  Downloading {filename}...")
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        tmp_path = tmp.name
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
            tmp.write(chunk)

    print(f"🔧 Enforcing schema...")
    # Read parquet with pandas and enforce types — same approach as DE Zoomcamp
    df = pd.read_parquet(tmp_path)

    # Apply dtypes where column exists
    for col, dtype in DTYPES.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype, errors="ignore")

    # Enforce datetime columns
    for col in DATE_COLS[taxi_type]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Write back to clean parquet
    clean_path = tmp_path + "_clean.parquet"
    df.to_parquet(clean_path, engine="pyarrow", index=False)
    os.unlink(tmp_path)

    print(f"⬆️  Uploading to GCS: {blob_path}")
    blob = bucket.blob(blob_path)
    blob.chunk_size = 8 * 1024 * 1024
    blob.upload_from_filename(clean_path, content_type="application/octet-stream")
    os.unlink(clean_path)
    print(f"✅ Done: {blob_path}\n")

if __name__ == "__main__":
    BUCKET = os.environ["GCS_BUCKET"]
    for taxi_type in ["yellow", "green"]:
        for month in range(1, 13):
            try:
                download_and_upload(taxi_type, 2019, month, BUCKET)
            except Exception as e:
                print(f"❌ Failed: {taxi_type} 2019-{month:02d} — {e}\n")
