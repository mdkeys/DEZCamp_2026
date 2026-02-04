-- Create an external table
CREATE OR REPLACE EXTERNAL TABLE `kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://kestra-sandbox-485519-hw3/yellow_tripdata_2024-0*.parquet']
);

-- Create non-partitioned table from the external table
CREATE OR REPLACE TABLE kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np AS
SELECT * FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3;

-- Q1: How many records? (20,332,093)
SELECT COUNT(*)
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np;

-- Q2: Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
-- 155.12 MB processed (156 billed) ESTIMATED for the materialized table
SELECT COUNT(DISTINCT PULocationID)
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np;

-- 0B ESTIMATED when run for external table. This is because BQ cannot estimate the amount of data in external tables. Also note that "Job Information" (what the actual compute/cost was) was NOT different from when I ran the query on the materialized vs external table. That's becaue it's the same data!
SELECT COUNT(DISTINCT PULocationID)
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3;

-- Q3: Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?
-- Answer #1: BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.

-- 155.12 MB
SELECT PULocationID
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np;
-- 310.24 MB 
SELECT PULocationID, DOLocationID
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np;

-- Q4: How many records have a fare_amount of 0? (8,333)
SELECT COUNT(*)
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np
WHERE fare_amount = 0;

-- Q5: What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy) [Answer: Partition by date, cluster by VendorID]
CREATE OR REPLACE TABLE kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_p
PARTITION BY DATE(tpep_dropoff_datetime) 
CLUSTER BY VendorID AS
SELECT * FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np;

-- Q6: Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive)
-- Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?

-- Not partitioned: 310.24 MB
SELECT DISTINCT VendorID
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_np
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' and '2024-03-15';

-- Partitioned: 26.84 MB
SELECT DISTINCT VendorID
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_p
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' and '2024-03-15';

-- Q7: Where is the data stored in the External Table you created? (GCP Bucket)
-- The query below confirms the table type is external. When you go to your GCP bucket, you will only see the underlying parquet files that make up the external table; there is NOT a new dataset/table saved in the bucket. 
-- Claude: The external table itself is just metadata in BigQuery that points to files in your GCS bucket
SELECT * FROM `kestra-sandbox-485519.zoomcamp.INFORMATION_SCHEMA.TABLES`
WHERE table_name = 'yellow_tripdata_hw3';

-- Q8: It is best practice in Big Query to always cluster your data. (FALSE)
-- Not for small data, frequently changing data (constantly updating), ad hoc analysis (use only once), or tables with diverse querying patterns (can only cluster on 4 columns max)

-- Q9: No Points: Write a SELECT count(*) query FROM the materialized table you created. How many bytes does it estimate will be read? Why?
-- 0B. Is it because it's already counted the number of rows for the table's metadata? (Checked with Claude and confirmed this is the case. It does not need to scan the table, it just pulls from the metadata already available).
SELECT COUNT(*)
FROM kestra-sandbox-485519.zoomcamp.yellow_tripdata_hw3_p;
