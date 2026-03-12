{{
  config(
    materialized = 'table',
    )
}}

SELECT 
pickup_date,
taxi_type,
pickup_borough,
COUNT(*) AS total_trips,
SUM(total_amount) AS total_revenue,
SUM(tip_amount) AS total_tips,
AVG(trip_distance) AS avg_distance,
AVG(trip_duration_min) AS avg_duration_min
FROM {{ ref('fct_trips') }}
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3