from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

# ─────────────────────────────────────────────
# 1. SET UP THE FLINK EXECUTION ENVIRONMENT
# ─────────────────────────────────────────────
# StreamExecutionEnvironment is the entry point for all Flink streaming jobs.
# set_parallelism(1) is required here because the green-trips3 topic only has
# 1 partition. With higher parallelism, idle consumer subtasks would prevent
# the watermark from advancing, meaning windows would never close.
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

# StreamTableEnvironment wraps the StreamExecutionEnvironment and adds
# SQL/Table API support, allowing us to write Flink jobs using SQL.
t_env = StreamTableEnvironment.create(env)

# ─────────────────────────────────────────────
# 2. DEFINE THE KAFKA SOURCE TABLE (DDL)
# ─────────────────────────────────────────────
# This CREATE TABLE statement tells Flink how to read from the green-trips3
# Kafka/Redpanda topic. It defines:
#   - The schema of the JSON messages coming in
#   - A computed column (event_timestamp) derived from lpep_pickup_datetime
#   - A watermark to handle late-arriving events (5 second tolerance)
#
# Key notes:
#   - lpep_pickup_datetime is read as VARCHAR (string) from JSON
#   - TO_TIMESTAMP converts it to a proper timestamp Flink can use for windowing
#   - The WATERMARK tells Flink how late events can arrive before a window closes.
#     Here we allow up to 5 seconds of lateness.
#   - bootstrap.servers uses redpanda:29092 (internal Docker network address),
#     NOT localhost:9092 which is only accessible from outside Docker
#   - scan.startup.mode = 'earliest-offset' means Flink reads all messages
#     from the beginning of the topic, not just new ones
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
        'properties.group.id' = 'flink-session-window',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'json'
    )
""")

# ─────────────────────────────────────────────
# 3. DEFINE THE POSTGRESQL SINK TABLE (DDL)
# ─────────────────────────────────────────────
# This CREATE TABLE statement tells Flink where to write results.
# It maps to the trips_session_window table we created in PostgreSQL.
#
# Key notes:
#   - TIMESTAMP(3) means millisecond precision timestamps
#   - PRIMARY KEY ... NOT ENFORCED is required by Flink's JDBC connector —
#     Flink uses it to perform upserts (insert or update) rather than
#     plain inserts, preventing duplicate rows if the job is restarted
#   - postgres:5432 is the internal Docker network address for PostgreSQL,
#     NOT localhost:5432
t_env.execute_sql("""
    CREATE TABLE trips_session_window (
        window_start TIMESTAMP(3),
        window_end TIMESTAMP(3),
        PULocationID INT,
        num_trips BIGINT,
        PRIMARY KEY (window_start, PULocationID) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = 'trips_session_window',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
""")

# ─────────────────────────────────────────────
# 4. DEFINE THE SESSION WINDOW AGGREGATION
# ─────────────────────────────────────────────
# This INSERT statement is the core of the job. It reads from green_trips,
# groups events into session windows per PULocationID, and writes results
# to trips_session_window in PostgreSQL.
#
# What is a session window?
#   Unlike tumbling windows (fixed size, e.g. every 5 minutes), a session
#   window groups events that arrive close together in time. The window stays
#   open as long as events keep arriving within the gap interval. When there's
#   a gap of more than 5 minutes with no events for a given PULocationID,
#   the window closes and the result is emitted.
#
# SESSION_START / SESSION_END extract the start and end timestamps of each
#   session window so we can see how long each session lasted.
#
# GROUP BY SESSION(...) + PULocationID means we get one row per session
#   per pickup location — so busy locations will have many sessions,
#   and quiet locations may have just one long one.
t_env.execute_sql("""
    INSERT INTO trips_session_window
    SELECT
        SESSION_START(event_timestamp, INTERVAL '5' MINUTE) AS window_start,
        SESSION_END(event_timestamp, INTERVAL '5' MINUTE) AS window_end,
        PULocationID,
        COUNT(*) AS num_trips
    FROM green_trips
    GROUP BY
        SESSION(event_timestamp, INTERVAL '5' MINUTE),
        PULocationID
""")