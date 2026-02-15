-- NOTE: For some reason this does not produce accurate queries. Use BQ to query the data.

/*
WITH cte_hw AS (
	SELECT * FROM {{ ref('fct_monthly_zone_revenue') }}
)

-- hw #3: 11,814 (when data was filtered for 2019-2020 data). Without filter it's 12,132 (even after I redownloaded the data)
select count(*)
from cte_hw
*/

SELECT count(*) 
FROM {{ ref('fct_monthly_zone_revenue') }}