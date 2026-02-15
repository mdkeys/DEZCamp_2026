# Homework 4

#1. If you run dbt run --select int_trips_unioned, what models will be built?
- int_trips_unioned only

#2. Your model fct_trips has been running successfully for months. A new value 6 now appears in the source data. What happens when you run dbt test --select fct_trips?
- dbt will fail the test, returning a non-zero exit code

#3. After running your dbt project, query the fct_monthly_zone_revenue model. What is the count of records in the fct_monthly_zone_revenue model?