from airflow.decorators import dag, task
from datetime import datetime
from airflow.models import Variable


# GCS_BUCKET = Variable.get("GCS_BUCKET")
# GCP_PROJECT_ID = Variable.get("GCP_PROJECT_ID")


@dag(
    dag_id = "nyc_taxi_pipeline",
    schedule= "0 6 1 * *", # At 06:00 on day-of-month 1
    start_date= datetime(2019, 1, 1),
    end_date= datetime(2019, 12, 1),
    catchup= True,
    max_active_runs= 1,
    tags= ["nyc", "taxi", "gcs", "etl"],
)
def nyc_taxi_pipeline():
    @task
    def ingest_yellow(logical_date=None):
        from scripts.ingest import download_and_upload
        download_and_upload(
            taxi_type="yellow",
            year=logical_date.year,
            month=logical_date.month,
            bucket_name=Variable.get("GCS_BUCKET")
        )

    @task
    def ingest_green(logical_date=None):
        from scripts.ingest import download_and_upload
        download_and_upload(
            taxi_type="green",
            year=logical_date.year,
            month=logical_date.month,
            bucket_name=Variable.get("GCS_BUCKET")
        )

    @task
    def load_yellow_to_bq(logical_date=None):
        from scripts.load_to_bq import load_month_to_bq
        load_month_to_bq(
            taxi_type="yellow",
            year=logical_date.year,
            month=logical_date.month
        )

    @task
    def load_green_to_bq(logical_date=None):
        from scripts.load_to_bq import load_month_to_bq
        load_month_to_bq(
            taxi_type="green",
            year=logical_date.year,
            month=logical_date.month
        )
    # Define task dependencies
    yellow_data = ingest_yellow()
    green_data = ingest_green()
    load_yellow = load_yellow_to_bq()
    load_green = load_green_to_bq()
    
    yellow_data >> load_yellow
    green_data >> load_green
    
nyc_taxi_pipeline()         
        