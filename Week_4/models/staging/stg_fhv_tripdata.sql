SELECT 
    -- identifiers 
    cast(dispatching_base_num as string) as dispatching_base_num,
    cast(PUlocationID as int) as pickup_location_id,
    cast(DOlocationID as int) as dropoff_location_id,

    -- timestamps 
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropOff_datetime as timestamp) as dropoff_datetime,

    -- trip info 
    cast(SR_Flag as int) as SR_Flag,
    cast(Affiliated_base_number as string) as Affiliated_base_number

FROM {{ source('raw_data', 'fhv_tripdata') }}

WHERE dispatching_base_num is not null