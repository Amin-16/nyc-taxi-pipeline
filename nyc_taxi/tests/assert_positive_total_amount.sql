-- This test fails if any trips have negative or zero total amount
-- Expected: 0 rows returned
SELECT *
FROM {{ ref('fct_trips') }}
WHERE total_amount <= 0
