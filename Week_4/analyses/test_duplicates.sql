-- Pull everything from int_trips_unioned
WITH cte_trips_unioned AS (
	SELECT * FROM {{ ref('int_trips_unioned') }}
),

-- identify duplicates & assign row numbers 
cte_dup_id AS (
    SELECT
        -- assign row number
        ROW_NUMBER() OVER(
            PARTITION BY 
                -- identifiers 
                vendor_id, rate_code_id, pickup_location_id, dropoff_location_id,
                -- timestamps
                pickup_datetime, dropoff_datetime,
                -- trip info
                store_and_fwd_flag, passenger_count, trip_type, --trip_distance, -- float64 cannot be partitioned
                -- financials
                fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, ehail_fee, total_amount, payment_type
            ORDER BY (SELECT NULL) -- Arbitrary ordering since rows are identical
        ) AS row_n,
        -- identify duplicates (1=yes, 0=no)
        CASE WHEN COUNT(*) OVER (
            PARTITION BY
                -- identifiers 
                vendor_id, rate_code_id, pickup_location_id, dropoff_location_id,
                -- timestamps
                pickup_datetime, dropoff_datetime,
                -- trip info
                store_and_fwd_flag, passenger_count, trip_type, --trip_distance, -- float64 cannot be partitioned
                -- financials
                fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, ehail_fee, total_amount, payment_type
            ) > 1 THEN 1 
            ELSE 0 
        END AS duplicate_n,
        * 
    FROM cte_trips_unioned
),

/* -- there are 215 rows that are part of a duplicate. Some of these have over 2 duplicate rows. 
SELECT *
FROM cte_dup_id
WHERE duplicate_n = 1 
*/

-- keep only the first instance of each duplicate
cte_dedup AS (
    SELECT *
    FROM cte_dup_id
    WHERE row_n = 1
)

-- select all and create trip_id by creating a row number (the issue with this method is the trip_id can change over time...)
SELECT
    ROW_NUMBER() OVER(ORDER BY (SELECT NULL)) AS trip_id,
    *
FROM cte_dedup


/* comment out 
-- Create "unique" trip ID
cte_tripid AS (
    SELECT 
        *,
        CAST(CONCAT(vendor_id,rate_code_id,pickup_location_id,dropoff_location_id,trip_distance,"_",pickup_datetime,dropoff_datetime,"_",total_amount) AS STRING) AS trip_id
    FROM cte_trips_unioned
    ORDER BY trip_id
)

-- Check for duplicates based on trip_id 
SELECT trip_id, trip_distance,
    COUNT(*) AS duplicate_count 
FROM cte_tripid
GROUP BY trip_id, trip_distance
ORDER BY duplicate_count DESC
*/


--NOTES:
-- The majority of the duplicates are because trip_distance = 0. In these cases, I imagine we want to drop the cases or only keep one instance. 
-- There are only 4 other trips that have 2 duplicate records each. In these cases, I imagine we want to drop one of the duplicates.

