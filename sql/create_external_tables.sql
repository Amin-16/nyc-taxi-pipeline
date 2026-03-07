-- External tables (reference layer — points to raw GCS files)
CREATE OR REPLACE EXTERNAL TABLE `nyc_taxi_raw.yellow_tripdata_2019_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://nyc-taxi-datalake-489001/raw/yellow/2019/*.parquet']
);

CREATE OR REPLACE EXTERNAL TABLE `nyc_taxi_raw.green_tripdata_2019_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://nyc-taxi-datalake-489001/raw/green/2019/*.parquet']
);
