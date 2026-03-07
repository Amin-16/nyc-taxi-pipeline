-- Native partitioned + clustered tables (working layer)
CREATE OR REPLACE TABLE `nyc_taxi_raw.yellow_tripdata_2019`
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY PULocationID, DOLocationID
AS SELECT * FROM `nyc_taxi_raw.yellow_tripdata_2019_external`;

CREATE OR REPLACE TABLE `nyc_taxi_raw.green_tripdata_2019`
PARTITION BY DATE(lpep_pickup_datetime)
CLUSTER BY PULocationID, DOLocationID
AS SELECT * FROM `nyc_taxi_raw.green_tripdata_2019_external`;
