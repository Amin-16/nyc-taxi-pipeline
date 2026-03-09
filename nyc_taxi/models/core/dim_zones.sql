{{
  config(
    materialized = 'table',
    )
}}
SELECT 
LocationID AS location_id,
Borough AS borough,
Zone AS zone,
service_zone
FROM {{ ref('taxi_zones') }}
WHERE Borough != 'Unknown' 