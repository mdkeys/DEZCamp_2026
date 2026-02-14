{% macro get_trip_id(vendor_id,rate_code_id,pickup_location_id,
                    dropoff_location_id,pickup_datetime,dropoff_datetime,
                    store_and_fwd_flag,passenger_count,trip_type,trip_distance,
                    fare_amount,extra,mta_tax,tip_amount,tolls_amount,improvement_surcharge,
                    ehail_fee,total_amount,payment_type) -%}

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
))

{%- endmacro %}
