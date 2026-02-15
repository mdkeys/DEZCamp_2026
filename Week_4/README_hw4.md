# Homework 4

#1. If you run dbt run --select int_trips_unioned, what models will be built?
- int_trips_unioned only

#2. Your model fct_trips has been running successfully for months. A new value 6 now appears in the source data. What happens when you run dbt test --select fct_trips?
- dbt will fail the test, returning a non-zero exit code

#3. After running your dbt project, query the fct_monthly_zone_revenue model. What is the count of records in the fct_monthly_zone_revenue model?
In BQ: 
`SELECT count(*) FROM `kestra-sandbox-485519.dezc_mod4.fct_monthly_zone_revenue`
- 12,184

#4. Using the fct_monthly_zone_revenue table, find the pickup zone with the highest total revenue (revenue_monthly_total_amount) for Green taxi trips in 2020. Which zone had the highest revenue?
In BQ: 
```
SELECT 
  pickup_zone, 
  SUM(revenue_monthly_total_amount) as revenue_2020_total
FROM `kestra-sandbox-485519.dezc_mod4.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND EXTRACT(YEAR FROM revenue_month) = 2020
GROUP BY pickup_zone
ORDER BY revenue_2020_total DESC
LIMIT 10
```
- East Harlem North	1817901.35

#5. Using the fct_monthly_zone_revenue table, what is the total number of trips (total_monthly_trips) for Green taxis in October 2019?
In BQ:
```
SELECT 
  service_type,
  revenue_month,
  SUM(total_monthly_trips) as sum_of_trips
FROM `kestra-sandbox-485519.dezc_mod4.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND revenue_month = '2019-10-01'
GROUP BY revenue_month, service_type
```
- Green	2019-10-01: 384,624

#6. Build a staging model for FHV Data 
- I used Kestra to load 2019 FHV trip data to dezc_mod4 in BQ 
- Staging model is under "staging" 
-  
