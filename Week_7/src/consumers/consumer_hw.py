import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from kafka import KafkaConsumer
from models_hw import ride_deserializer

server = 'localhost:9092'
topic_name = 'green-trips3'

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='postgres',
    user='postgres',
    password='postgres'
)
conn.autocommit = True # Enable autocommit mode so we don't have to manually commit after each insert.
cur = conn.cursor()

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[server],
    auto_offset_reset='earliest',
    group_id='rides-to-postgres-2',
    value_deserializer=ride_deserializer,
    consumer_timeout_ms=10000 # Add this so that it times out after 10 seconds, otherwise it will wait indefinitely. 
)

print(f"Listening to {topic_name} and writing to PostgreSQL...")

# Read messages and insert into postgres into the processed_events table. 
# We convert the pickup and dropoff datetimes from epoch milliseconds to Python datetime objects before inserting.
count = 0
for message in consumer:
    ride = message.value
    pickup_dt = datetime.fromtimestamp(ride.lpep_pickup_datetime / 1000)
    dropoff_dt = datetime.fromtimestamp(ride.lpep_dropoff_datetime / 1000)
    cur.execute( # This is a parameterized query to safely insert data into PostgreSQL, preventing SQL injection.
        """INSERT INTO processed_events 
           (PULocationID, DOLocationID, passenger_count, trip_distance, tip_amount, total_amount, pickup_datetime, dropoff_datetime)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (ride.PULocationID, ride.DOLocationID, ride.passenger_count, ride.trip_distance, ride.tip_amount, ride.total_amount, pickup_dt, dropoff_dt)
    )
    count += 1
    if count % 100 == 0:
        print(f"Inserted {count} rows...")

print(f"Total trips: {count}")

consumer.close()
cur.close()
conn.close()