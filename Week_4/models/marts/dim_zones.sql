WITH taxi_zone_lookup AS (
    SELECT * FROM {{ ref('taxi_zone_lookup') }}
	),

-- rename some of the columns
renamed AS (
	SELECT 
        locationid AS location_id,
		borough, 
        zone, 
        service_zone
		FROM taxi_zone_lookup
	)
		
SELECT * FROM renamed