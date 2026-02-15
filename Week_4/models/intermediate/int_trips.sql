-- Enrich and deduplicate the trip data 
-- For ease of homework, limit the dataset to 2019 & 2020 trips only 

WITH cte_unioned AS (
    SELECT * FROM {{ ref('int_trips_unioned')}}
    -- WHERE EXTRACT(YEAR FROM pickup_datetime) IN (2019, 2020) -- Comment out based on feedback in slack: https://datatalks-club.slack.com/archives/C01FABYF2RG/p1771005143846579?thread_ts=1770992097.472379&cid=C01FABYF2RG 
),

/* -- Comment out CTE from DEZC example on pts. Look at DEZC for their final file. */

cte_cleaned_enriched AS (
    SELECT 
        /* Comment out my original trip_id using the macro. It's not as clean as trip_id using generate_surrogate_key. 
        -- I confirmed both methods of trip_id result in the same output. 
        -- unique trip ID (uses ALL factors) based on the macro I created -- do this for testing against trip_id2
        {{ get_trip_id('vendor_id','rate_code_id','pickup_location_id',
                    'dropoff_location_id','pickup_datetime','dropoff_datetime',
                    'store_and_fwd_flag','passenger_count','trip_type','trip_distance',
                    'fare_amount','extra','mta_tax','tip_amount','tolls_amount',
                    'improvement_surcharge','ehail_fee','total_amount','payment_type') 
        }} as trip_id2,
        */

        -- unique trip ID. Note: Using example from DEZC file to test the package and compare end "qualify" function
        {{ dbt_utils.generate_surrogate_key(['u.vendor_id', 'u.pickup_datetime', 'u.pickup_location_id', 'u.service_type']) }} as trip_id,

        -- Identifiers
        u.vendor_id,
        u.service_type,
        u.rate_code_id,

        -- Location IDs
        u.pickup_location_id,
        u.dropoff_location_id,

        -- Timestamps
        u.pickup_datetime,
        u.dropoff_datetime,

        -- Trip details
        u.store_and_fwd_flag,
        u.passenger_count,
        u.trip_distance,
        u.trip_type,

        -- Payment breakdown
        u.fare_amount,
        u.extra,
        u.mta_tax,
        u.tip_amount,
        u.tolls_amount,
        u.ehail_fee,
        u.improvement_surcharge,
        u.total_amount,

        -- Enrich with payment type description
        coalesce(u.payment_type, 0) as payment_type,    -- if payment_type is NULL, treat as 0 and description = Unknown
        -- coalesce(pt.description, 'Unknown') as payment_type_description     -- if no match found, description = unknown. Comment out and replace with macro
        {{ get_payment_type('u.payment_type') }} as payment_type_description

    from cte_unioned AS u
    -- left join cte_payment_types AS pt                    -- no cte to join
    --    on coalesce(u.payment_type, 0) = pt.payment_type  -- no cte to join 
),

cte_final AS (
select * from cte_cleaned_enriched

-- Deduplicate: if multiple trips match (same vendor, second, location, service), keep first
-- qualify = "where" for window functions like over()
qualify row_number() over(
    partition by vendor_id, pickup_datetime, pickup_location_id, service_type   -- can't this just be trip_id? I tested and it's the same result. 
    order by dropoff_datetime
) = 1
)

select * from cte_final

/*
-- Confirm the date limit worked 
SELECT count(*) as dup_n, EXTRACT(YEAR FROM pickup_datetime) as year_pu 
FROM cte_temp 
GROUP BY year_pu 
*/
