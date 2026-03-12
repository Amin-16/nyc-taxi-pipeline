{{
  config(
    materialized = 'table',
    )
}}

SELECT    
pickup_borough,
pickup_zone,
taxi_type,
COUNT(*) AS total_trips,
SUM(total_amount) AS total_revenue,
AVG(trip_distance) AS avg_distance,
AVG(trip_duration_min) AS avg_duration_min,
AVG(tip_amount) AS avg_tip

FROM {{ ref('fct_trips') }}
GROUP BY 1, 2, 3
ORDER BY total_revenue DESC
