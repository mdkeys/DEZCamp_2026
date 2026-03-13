# For week 7 homework:
https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/07-streaming/homework.md 

## Q1: 
1. Restart docker containers: `Docker compose up -d`
2. Reconnect to postgress: `uvx pgcli -h localhost -p 5432 -U postgres -d postgres`
3. Run commands to (1) see the help options for redpanda and (2) see the version of redpanda
   1. `docker exec -it week_7-redpanda-1 rpk help`
   2. `docker exec -it week_7-redpanda-1 rpk version`

Answer:  v25.3.9

## Q2: 
1. Create 'green-trips' topic: `docker exec -it week_7-redpanda-1 rpk topic create green-trips`
2. Run: `uv run python src/producers/producer_hw2.py` to run the producer file
   1. Note: This ONLY converts to dictionary before sending to topic 'green-trips'
   2. Note: It initially failed because there are NaN (missing) values in the count of participants. I had to adjust the models_hw.py file to account for this. I also dropped and re-created the 'green-trips' topic to avoid duplicating the trips inserted. 
      1. To delete the topic: `docker exec -it week_7-redpanda-1 rpk topic delete green-trips`
      2. To confirm what topics are available, use 'list': `docker exec -it week_7-redpanda-1 rpk topic list`

Answer: ~10 seconds

## Q3:
1. Create 'consumer_hw3.py'
2. Run: `uv run python src/consumers/consumer_hw3.py`

Note: You can also run this another way by doing the full processing with the Ride dataclass like we did in the workshop.
Using 'producer_hw.py', 'consumer_hw.py', and 'models_hw.py':
1. First, set up a table in postgres:
    ```sql 
    CREATE TABLE IF NOT EXISTS processed_events (
        PULocationID INT,
        DOLocationID INT,
        passenger_count INT,
        trip_distance FLOAT,
        tip_amount FLOAT,
        total_amount FLOAT,
        pickup_datetime TIMESTAMP,
        dropoff_datetime TIMESTAMP
    );
    ```
2. Create topic 'green-trips3' (to not interfere with the existing 'green-trips' topic): `docker exec -it week_7-redpanda-1 rpk topic create green-trips3`
3. Run producer_hw: `uv run python src/producers/producer_hw.py` (this sends 49k+ rows and took 615.01 seconds)
4. Run consumer_hw: `uv run python src/consumers/consumer_hw.py`
   1. Note: If you have to re-run this to fix anything, you need to change the 'group_id'. Otherwise it won't read the data it already read in. 
   2. Note: I added a timeout function (consumer_timeout_ms) so that it would stop running after not receiving more data after 10 seconds. This way the process would end and would output the count.
5. Go into postgress and run: 
   1. Count # rows in table: `SELECT count(*) from processed_events`
   2. Count # trips where distance > 5km: `SELECT count(*) from processed_events where trip_distance > 5`

Answer: 8506


**Note: For the following exercises, I asked Claude to create the Flink files.**

## Q4: 
1. Updated 'models_hw.py' to convert lpep timestamps into string for Flink DDS to use
2. In Postgres, create a table for consumer to put data into:
   ```sql
   CREATE TABLE IF NOT EXISTS trips_per_pulocation (
        window_start TIMESTAMP,
        PULocationID INT,
        num_trips BIGINT,
        PRIMARY KEY (window_start, PULocationID)
    );
   ```
3. Create the Flink job 'trips_per_pulocation.py'
4. Dropped & recreated topic 'green-trips3'
5. Reran producer_hw: `uv run python src/producers/producer_hw.py`
6. Submitted the Flink job: `docker exec -it week_7-jobmanager-1 flink run -py /opt/src/job/trips_per_pulocation.py`
7. Query results in postgress:
    ```sql
    SELECT PULocationID, num_trips
    FROM trips_per_pulocation
    ORDER BY num_trips DESC
    LIMIT 3;
    ```

Answer: 74
Output: 
```
+--------------+-----------+
| pulocationid | num_trips |
|--------------+-----------|
| 74           | 15        |
| 74           | 14        |
| 74           | 13        |
+--------------+-----------+
```
Count of rows: 23312

## Q5: 
1. Create table in postgress:
    ```sql
    CREATE TABLE IF NOT EXISTS trips_session_window (
        window_start TIMESTAMP,
        window_end TIMESTAMP,
        PULocationID INT,
        num_trips BIGINT,
        PRIMARY KEY (window_start, PULocationID)
    );
    ```
2. Create 'trips_session_window.py'
3. Submit the Flink job: `docker exec -it week_7-jobmanager-1 flink run -py /opt/src/job/trips_session_window.py`
4. Run SQL query:
    ```sql
    SELECT window_start, window_end, PULocationID, num_trips
    FROM trips_session_window
    ORDER BY num_trips DESC
    LIMIT 5;
    ```

Answer: 81
Output: 
```
+---------------------+---------------------+--------------+-----------+
| window_start        | window_end          | pulocationid | num_trips |
|---------------------+---------------------+--------------+-----------|
| 2025-10-08 06:46:14 | 2025-10-08 08:27:40 | 74           | 81        |
| 2025-10-01 06:52:23 | 2025-10-01 08:23:33 | 74           | 72        |
| 2025-10-22 06:58:31 | 2025-10-22 08:25:04 | 74           | 71        |
| 2025-10-28 08:31:08 | 2025-10-28 09:39:30 | 74           | 71        |
| 2025-10-27 06:56:30 | 2025-10-27 08:24:09 | 74           | 70        |
+---------------------+---------------------+--------------+-----------+
```
Count of rows: 24441
Note: The count of rows in the table are the number of session windows. 


## Q6:
1. Create table in postgress:
    ```sql
    CREATE TABLE IF NOT EXISTS trips_tip_per_hour (
        window_start TIMESTAMP,
        total_tip FLOAT,
        PRIMARY KEY (window_start)
    );
    ```
2. Create 'trips_tip_per_hour.py'
3. Submit the Flink job: `docker exec -it week_7-jobmanager-1 flink run -py /opt/src/job/trips_tip_per_hour.py`

Answer: 2025-10-16 18:00:00
Output: 
```
+---------------------+-------------------+
| window_start        | total_tip         |
|---------------------+-------------------|
| 2025-10-16 18:00:00 | 510.8600158691406 |
| 2025-10-30 16:00:00 | 494.4099426269531 |
| 2025-10-10 17:00:00 | 470.0800476074219 |
| 2025-10-16 17:00:00 | 445.010009765625  |
| 2025-10-02 17:00:00 | 439.5400085449219 |
+---------------------+-------------------+
```

Count of table rows: 657

## Clean up
1. Remove all containers: `docker compose down`
2. Remove PostgresSQL data volume: `docker compose down -v`
3. Check if anything is still running: `docker ps`
4. Check all stopped containers: `docker ps -a`