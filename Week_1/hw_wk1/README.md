# Week 1 Homework
For https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/01-docker-terraform/homework.md 

## Q1:
Code: #Remember to open Docker desktop first
`docker run -it --rm --entrypoint=bash python:3.13
pip -V   ## don't do python -v (verbose)
exit`

- Anwer: pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)

## Q2: 
- Answer: hostname=db (container name=postgres) & port=5432 (5433 is the localhost)

## Q3: 
Code:
`SELECT COUNT(*)
FROM green_tripdata
WHERE DATE(lpep_pickup_datetime) >= '2025-11-01' 
  AND DATE(lpep_pickup_datetime) < '2025-12-01'
  AND trip_distance <= 1;`

- Answer: 8007

## Q4: 
Code:
`SELECT lpep_pickup_datetime, trip_distance
FROM green_tripdata
WHERE trip_distance < 100
ORDER BY trip_distance DESC;`

- Answer: 2025-11-14

## Q5: 
Code:
`WITH top_pickup AS (
    SELECT 
        SUM(total_amount) AS sum_of_total, 
        "PULocationID"
    FROM green_tripdata
    WHERE DATE(lpep_pickup_datetime) = '2025-11-18' 
    GROUP BY "PULocationID"
    ORDER BY sum_of_total DESC
    LIMIT 1
)
SELECT z.*
FROM taxi_zones z
JOIN top_pickup t ON z."LocationID" = t."PULocationID";`

- Answer: 74 - East Harlem North

## Q6: 
Code:
`WITH v1 AS (
SELECT g.lpep_dropoff_datetime, g."DOLocationID", g."PULocationID", g.tip_amount
FROM green_tripdata AS g
JOIN taxi_zones AS t
ON g."PULocationID" = t."LocationID"
WHERE g.lpep_dropoff_datetime >= '2025-11-01' 
  AND g.lpep_dropoff_datetime < '2025-12-01'
  AND t."Zone" = 'East Harlem North'
ORDER BY g.tip_amount DESC
LIMIT 1
)`

`SELECT "LocationID", "DOLocationID", "Zone"
FROM taxi_zones AS t
JOIN v1 ON v1."DOLocationID" = t."LocationID";`

- Answer: 263 - Yorkville West

## Q7: cd to terrademo1 folder (entire folder set to ignored by git)
- Ran commands from https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform/terraform/terraform#execution
- Review commands: https://developer.hashicorp.com/terraform/cli/run
- Answer: `terraform init`, `terraform apply -auto-approve`, `terraform destroy`


# Summary of what I did (I need to double-check the order of operations):
- Created data ingestion script (hw_ingest_data.py) and Dockerfile. 
  - *The .ipynb file was my draft to create the hw_ingest_data.py. I used Claude.ai to help transform it and provide click commands. The initial prompt I used on Claude.ai was*: 
  
    *"Clean up the following file so that it will work when run through a Dockerfile. Also add use click to parse the arguments." [Attached the code from my .ipynb file]* 
  - *Note that I had used several prompts prior to this to work through examples, so it's possible it fed off prior examples. See "Homework 1 ZoomCamp" chat in Claude for prompt history.*
- Confirmed the data ingest worked using pgcli 
- Set up Docker containers for PostgreSQL and pgAdmin (docker-compose.yaml)
- Created Docker image (Dockerfile) (`docker build`)
- Loaded green taxi and zones data into PostgreSQL (had to remove SSL verify):
  `docker run -it \
  --network=hw_wk1_default \
  hw_ingest:v001 \
  --user=root \
  --password=root \
  --host=pgdatabase \
  --port=5432 \
  --db=ny_taxi \
  --url-green=https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet \
  --url-zones=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv \
  --table-green=green_tripdata \
  --table-zones=taxi_zones \
  --chunksize=50000 \
  --disable-ssl-verify`
- Completed SQL queries in pgAdmin

### Instructions to re-launch (NOTE: This needs to be corrected)
1. Start Docker: `docker compose up -d`
2. Access pgAdmin: http://localhost:8085 (admin@admin.com / root)
3. Run ingestion: `uv run python hw_ingest_data.py --host=localhost --url-green=... --url-zones=... --disable-ssl-verify`

### Notes from issues I encountered:
- Remember to use double quotes for column names in SQL: "PULocationID"
- Use single quotes for string values: 'Newark Airport'
- SSL verification needs to be disabled for cloudfront URLs
