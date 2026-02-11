## Module 2 homework
https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/02-workflow-orchestration/homework.md

**Note:** 
- I used the 09_gcp_taxi_scheduled.yaml under Week_2/flows with the docker-compose.yaml under Week_2. I did not make copies in this homework folder, but you can go up a level to see those files.
- **If you want to spin up Kestra again & load data into BQ** Remember to run flow "06_gcp_kv.yaml" to add your key values before you execute a new flow to load data into your BQ bucket. 

## Q1: Yellow_2020-12 (uncompressed file size of the extract task)
I used the 09_gcp_taxi_scheduled.yaml file and ran a backfill for 2020-12-01. Then I checked BigQuery for the datasize of file yellow_tripdata_2020-12.csv (go to Details tab). But that shows the size (334.43 MB).

Instead, when you go to the Execution > go to "Metrics" and find the "upload_to_gcs" task. The name of the metric is "file.size" and the "value" is the size.

- Answer: 134.5 MB (134,481,400)

Note: Alternative method is to remove PurgeCurrentExecutionFiles at the end of the flow. When you purge them, you can't preview or see their file size in the "Outputs" tab of Kestra.

## Q2: Green -- 2020-04
- Answer: green_tripdata_2020-04.csv

## Q3: Yellow -- all 2020 (count of rows)
yellow_tripdata in BigQuery will have all of the data across all files loaded. 

```sql
SELECT COUNT(*) 
FROM `kestra-sandbox-485519.zoomcamp.yellow_tripdata`
WHERE filename LIKE "yellow_tripdata_2020%";
```

- Answer: 24,648,499

## Q4: Green -- all 2020 (count of rows)
green_tripdata in BigQuery will have all of the data across all files loaded. Note: I loaded 2020 data for Green first, so I did not have to use the query below. Instead, I was able to look at the Details tab of green_tripdata.

```sql
SELECT COUNT(*) 
FROM `kestra-sandbox-485519.zoomcamp.green_tripdata`
WHERE filename LIKE "green_tripdata_2020%";
```

- Answer: 1,734,051

## Q5: Yellow -- 2021-03 (count of rows)
You can query
```sql
SELECT COUNT(*) 
FROM `kestra-sandbox-485519.zoomcamp.yellow_tripdata_2021_03`;
```
or you can just look at the Details tab of the CSV file. It's probably better NOT to query to save credits. Oops.

- Answer: 1.93M (1,925,152)

## Q6: 
- Answer: timezone: "America/New_York"

*See 09_gcp_taxi_scheduled.yaml for an example. I had to change it to America/New_York because it was set to UTC (behind by 5 hours) in Kestra.*
