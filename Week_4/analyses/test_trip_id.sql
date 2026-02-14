-- Pull everything from int_trips_unioned
WITH cte_trips_unioned AS (
	SELECT * FROM {{ ref('int_trips_unioned') }}
),

-- Create trip_id based on MD5 hash. This will create the same trip_id for duplicate rows.

cte_trip_id AS (
    SELECT 
       MD5(CONCAT( -- need to cast as STRING and use '|' to ensure inputs are unique
        COALESCE(CAST(vendor_id AS STRING), ''), '|',
        COALESCE(CAST(rate_code_id AS STRING), ''), '|',
        COALESCE(CAST(pickup_location_id AS STRING), ''), '|',
        COALESCE(CAST(dropoff_location_id AS STRING), ''), '|',
        COALESCE(CAST(pickup_datetime AS STRING), ''), '|',
        COALESCE(CAST(dropoff_datetime AS STRING), ''), '|',
        COALESCE(CAST(store_and_fwd_flag AS STRING), ''), '|',
        COALESCE(CAST(passenger_count AS STRING), ''), '|',
        COALESCE(CAST(trip_type AS STRING), ''), '|',
        COALESCE(CAST(trip_distance AS STRING), ''), '|',
        COALESCE(CAST(fare_amount AS STRING), ''), '|',
        COALESCE(CAST(extra AS STRING), ''), '|',
        COALESCE(CAST(mta_tax AS STRING), ''), '|',
        COALESCE(CAST(tip_amount AS STRING), ''), '|',
        COALESCE(CAST(tolls_amount AS STRING), ''), '|',
        COALESCE(CAST(improvement_surcharge AS STRING), ''), '|',
        COALESCE(CAST(ehail_fee AS STRING), ''), '|',
        COALESCE(CAST(total_amount AS STRING), ''), '|',
        COALESCE(CAST(payment_type AS STRING), '')
       )) AS trip_id,
        *
    FROM cte_trips_unioned
)

SELECT trip_id, count(*) as dup_n
FROM cte_trip_id
GROUP BY trip_id
ORDER BY dup_n DESC