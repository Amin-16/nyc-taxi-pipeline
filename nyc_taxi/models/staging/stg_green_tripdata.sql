{{ config(materialized='view') }}

SELECT
    -- identifiers
    CAST(vendorid AS INTEGER)           AS vendor_id,
    CAST(ratecodeid AS INTEGER)         AS rate_code_id,
    CAST(pulocationid AS INTEGER)       AS pickup_location_id,
    CAST(dolocationid AS INTEGER)       AS dropoff_location_id,

    -- timestamps
    CAST(lpep_pickup_datetime AS TIMESTAMP)     AS pickup_datetime,
    CAST(lpep_dropoff_datetime AS TIMESTAMP)    AS dropoff_datetime,

    -- trip info
    CAST(store_and_fwd_flag AS STRING)  AS store_and_fwd_flag,
    CAST(passenger_count AS INTEGER)    AS passenger_count,
    CAST(trip_distance AS NUMERIC)      AS trip_distance,

    -- payment info
    CAST(fare_amount AS NUMERIC)            AS fare_amount,
    CAST(extra AS NUMERIC)                  AS extra,
    CAST(mta_tax AS NUMERIC)                AS mta_tax,
    CAST(tip_amount AS NUMERIC)             AS tip_amount,
    CAST(tolls_amount AS NUMERIC)           AS tolls_amount,
    CAST(improvement_surcharge AS NUMERIC)  AS improvement_surcharge,
    CAST(total_amount AS NUMERIC)           AS total_amount,
    CAST(congestion_surcharge AS NUMERIC)   AS congestion_surcharge,
    CAST(payment_type AS INTEGER)           AS payment_type,
    CAST(trip_type AS INTEGER)              AS trip_type,
    CAST(ehail_fee AS NUMERIC)              AS ehail_fee,

    -- taxi type identifier
    'green' AS taxi_type

FROM {{ source('nyc_taxi_raw', 'green_tripdata_2019') }}

WHERE CAST(lpep_pickup_datetime AS TIMESTAMP) >= '2019-01-01'
  AND CAST(lpep_pickup_datetime AS TIMESTAMP) < '2020-01-01'
  AND total_amount > 0
  AND trip_distance > 0
  AND vendorid IS NOT NULL
