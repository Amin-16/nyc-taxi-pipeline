{{
  config(
    materialized = 'table',
    )
}}

SELECT 
pickup_hour,
pickup_day_of_week,
taxi_type,
COUNT(*)  as trip_count,
AVG(trip_duration_min) as avg_trip_duration,
AVG(trip_distance)    as avg_trip_distance,
SUM(total_amount)     as total_revenue,
AVG(total_amount)     as avg_fare
FROM {{ ref('fct_trips') }}
GROUP BY 1, 2, 3
