-- Basic stats
SELECT
  COUNT(*)                          AS total_trips,
  ROUND(SUM(total_amount), 2)       AS total_revenue,
  ROUND(AVG(trip_distance), 2)      AS avg_distance_miles,
  ROUND(AVG(total_amount), 2)       AS avg_fare,
  ROUND(AVG(passenger_count), 2)    AS avg_passengers,
  MIN(DATE(tpep_pickup_datetime))   AS first_trip,
  MAX(DATE(tpep_pickup_datetime))   AS last_trip
FROM `nyc_taxi_raw.yellow_tripdata_2019`;

-- Revenue by month
SELECT
  EXTRACT(MONTH FROM tpep_pickup_datetime)  AS month,
  COUNT(*)                                  AS total_trips,
  ROUND(SUM(total_amount), 2)               AS total_revenue
FROM `nyc_taxi_raw.yellow_tripdata_2019`
GROUP BY 1
ORDER BY 1;

-- Data quality check — dirty timestamps
-- Results: 84,597,002 valid | 994 before 2019 | 448 after 2019
SELECT
  COUNT(*) AS total_trips,
  COUNTIF(DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-12-31') AS valid_trips,
  COUNTIF(DATE(tpep_pickup_datetime) < '2019-01-01') AS trips_before_2019,
  COUNTIF(DATE(tpep_pickup_datetime) > '2019-12-31') AS trips_after_2019
FROM `nyc_taxi_raw.yellow_tripdata_2019`;
