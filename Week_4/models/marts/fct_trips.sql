WITH trips_unioned AS (
	SELECT * FROM {{ ref('int_trips_unioned') }}
),

cte_trip_id AS (
	SELECT 
        {{ get_trip_id('vendor_id','rate_code_id','pickup_location_id',
                    'dropoff_location_id','pickup_datetime','dropoff_datetime',
                    'store_and_fwd_flag','passenger_count','trip_type','trip_distance',
                    'fare_amount','extra','mta_tax','tip_amount','tolls_amount',
                    'improvement_surcharge','ehail_fee','total_amount','payment_type') 
        }} as trip_id
	FROM trips_unioned
)

SELECT *, count(*) as dup_n
FROM cte_trip_id
GROUP BY trip_id
ORDER BY dup_n DESC 