import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

import argparse 

# Use this for command line arguments. You can also just set the variables 'input_green', 'input_yellow', and 'output' to the paths you want to use.
parser = argparse.ArgumentParser()

parser.add_argument('--input_green', required=True)
parser.add_argument('--input_yellow', required=True)
parser.add_argument('--output', required=True)

args = parser.parse_args()

input_green = args.input_green
input_yellow = args.input_yellow
output = args.output

spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()

# Use the Cloud Storage bucket for temporary BigQuery export data used
# by the connector.
spark.conf.set('temporaryGcsBucket', 'dataproc-staging-us-east1-317513627238-f7vgihwy')

# Read in green data
df_green = spark.read.parquet(input_green)

# Read in yellow data
df_yellow = spark.read.parquet(input_yellow)

# Rename the datetime columns so that they have the same name in both datasets
df_green = df_green \
    .withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('lpep_dropoff_datetime', 'dropoff_datetime')

df_yellow = df_yellow \
    .withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('tpep_dropoff_datetime', 'dropoff_datetime')

# Only shows columns that exist in both sets
set(df_green.columns) & set(df_yellow.columns)

# Preserve the order of columns so that the datetime columns are after VendorID
common_columns = []

yellow_columns = set(df_yellow.columns)

for col in df_green.columns:
    if col in yellow_columns:
        common_columns.append(col)

# We want to select the common columns from both datasets
# But we also need to know which dataset they came from
# So we're going to select the common columns AND add a var 'service_type' to show green or yellow

df_green_sel = df_green \
    .select(common_columns) \
    .withColumn('service_type', F.lit('green')) #F.lit is a function 'literal'

df_yellow_sel = df_yellow \
    .select(common_columns) \
    .withColumn('service_type', F.lit('yellow')) #F.lit is a function 'literal'

# Create shared df 'trips_data' that unions yellow_sel and green_sel (all rows combined)
df_trips_data = df_green_sel.unionAll(df_yellow_sel)

# Now we can count the number of rows by service_type
df_trips_data.groupBy('service_type').count().show()

# Now we want to use SQL. We need to convert the df into a temp table for use:
# Note: 'registerTempTable' is deprecated. Need to use createOrReplaceTempView
df_trips_data.createOrReplaceTempView('trips_data')

# Write your SQL code
# Now we can execute a large SQL query and save it as a dataframe:
df_result = spark.sql("""
SELECT 
    -- Reveneue grouping 
    PULocationID AS revenue_zone,
    date_trunc('month', pickup_datetime) AS revenue_month, 
    service_type, 

    -- Revenue calculation 
    SUM(fare_amount) AS revenue_monthly_fare,
    SUM(extra) AS revenue_monthly_extra,
    SUM(mta_tax) AS revenue_monthly_mta_tax,
    SUM(tip_amount) AS revenue_monthly_tip_amount,
    SUM(tolls_amount) AS revenue_monthly_tolls_amount,
    SUM(improvement_surcharge) AS revenue_monthly_improvement_surcharge,
    SUM(total_amount) AS revenue_monthly_total_amount,
    SUM(congestion_surcharge) AS revenue_monthly_congestion_surcharge,

    -- Additional calculations
    AVG(passenger_count) AS avg_montly_passenger_count,
    AVG(trip_distance) AS avg_montly_trip_distance
FROM
    trips_data
GROUP BY
    1, 2, 3
""")

# Check the number of rows in the result
df_result.count()


# Save the data to BigQuery
df_result.write.format('bigquery') \
  .option('table', output) \
  .save()