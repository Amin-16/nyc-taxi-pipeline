from google.cloud import bigquery
import os

def get_client():
    return bigquery.Client()

def load_month_to_bq(taxi_type: str, year: int, month: int):
    """Load single month from GCS → BigQuery. Called by Airflow task."""
    client = get_client()
    bucket = os.environ["GCS_BUCKET"]
    project = client.project

    gcs_path = f"gs://{bucket}/raw/{taxi_type}/{year}/{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    table_id = f"{project}.nyc_taxi_raw.{taxi_type}_tripdata_{year}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    print(f"📦 Loading {taxi_type} {year}-{month:02d} → BigQuery...")
    load_job = client.load_table_from_uri(gcs_path, table_id, job_config=job_config)
    load_job.result()
    print(f"✅ Loaded: {taxi_type} {year}-{month:02d}")

def create_external_table(taxi_type: str, year: int):
    """Reference layer — points to raw GCS files."""
    client = get_client()
    bucket = os.environ["GCS_BUCKET"]
    project = client.project

    table_id = f"{project}.nyc_taxi_raw.{taxi_type}_tripdata_{year}_external"
    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = [f"gs://{bucket}/raw/{taxi_type}/{year}/*.parquet"]
    external_config.autodetect = True
    table = bigquery.Table(table_id)
    table.external_data_configuration = external_config
    client.delete_table(table_id, not_found_ok=True)
    client.create_table(table)
    print(f"✅ External table created: {table_id}")

if __name__ == "__main__":
    for taxi_type in ["yellow", "green"]:
        create_external_table(taxi_type, 2019)
        client = get_client()
        client.delete_table(f"{client.project}.nyc_taxi_raw.{taxi_type}_tripdata_2019", not_found_ok=True)
        for month in range(1, 13):
            try:
                load_month_to_bq(taxi_type, 2019, month)
            except Exception as e:
                print(f"❌ Failed {taxi_type} {month}: {e}")
