from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

# ─────────────────────────────────────────────
# 1. SET UP THE FLINK EXECUTION ENVIRONMENT
# ─────────────────────────────────────────────
# set_parallelism(1) is required because green-trips3 has only 1 partition.
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)

# ─────────────────────────────────────────────
# 2. DEFINE THE KAFKA SOURCE TABLE
# ─────────────────────────────────────────────
# Same source DDL as previous jobs — reads from green-trips3 topic.
# We only need tip_amount and event_timestamp for this job but define
# all columns to match the JSON message schema.
t_env.execute_sql("""
    CREATE TABLE green_trips (
        lpep_pickup_datetime VARCHAR,
        lpep_dropoff_datetime VARCHAR,
        PULocationID INT,
        DOLocationID INT,
        passenger_count INT,
        trip_distance FLOAT,
        tip_amount FLOAT,
        total_amount FLOAT,
        event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
        WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'green-trips3',
        'properties.bootstrap.servers' = 'redpanda:29092',
        'properties.group.id' = 'flink-tip-per-hour',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'json'
    )
""")

# ─────────────────────────────────────────────
# 3. DEFINE THE POSTGRESQL SINK TABLE
# ─────────────────────────────────────────────
# One row per hour — window_start is the primary key since each
# 1-hour tumbling window has a unique start time.
t_env.execute_sql("""
    CREATE TABLE trips_tip_per_hour (
        window_start TIMESTAMP(3),
        total_tip FLOAT,
        PRIMARY KEY (window_start) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = 'trips_tip_per_hour',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
""")

# ─────────────────────────────────────────────
# 4. DEFINE THE TUMBLING WINDOW AGGREGATION
# ─────────────────────────────────────────────
# Groups all trips into 1-hour tumbling windows regardless of location,
# summing tip_amount across all trips in that hour.
# Unlike the session window job, there is no GROUP BY PULocationID here
# since we want totals across all locations per hour.
t_env.execute_sql("""
    INSERT INTO trips_tip_per_hour
    SELECT
        TUMBLE_START(event_timestamp, INTERVAL '1' HOUR) AS window_start,
        CAST(SUM(tip_amount) AS FLOAT) AS total_tip
    FROM green_trips
    GROUP BY
        TUMBLE(event_timestamp, INTERVAL '1' HOUR)
""")