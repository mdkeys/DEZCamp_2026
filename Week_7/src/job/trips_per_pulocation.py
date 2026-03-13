from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)

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
        'topic' = 'green-trips',
        'properties.bootstrap.servers' = 'redpanda:29092',
        'properties.group.id' = 'flink-green-trips',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'json'
    )
""")

t_env.execute_sql("""
    CREATE TABLE trips_per_pulocation (
        window_start TIMESTAMP(3),
        PULocationID INT,
        num_trips BIGINT,
        PRIMARY KEY (window_start, PULocationID) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = 'trips_per_pulocation',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
""")

t_env.execute_sql("""
    INSERT INTO trips_per_pulocation
    SELECT
        TUMBLE_START(event_timestamp, INTERVAL '5' MINUTE) AS window_start,
        PULocationID,
        COUNT(*) AS num_trips
    FROM green_trips
    GROUP BY
        TUMBLE(event_timestamp, INTERVAL '5' MINUTE),
        PULocationID
""")