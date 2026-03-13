import sys
from datetime import datetime
from pathlib import Path

# We need to add the parent directory of this notebook to the Python path so we can import our models module.
sys.path.insert(0, str(Path(__file__).parent.parent))

from kafka import KafkaConsumer
from models import ride_deserializer

# Define the Kafka server and topic we want to consume from. 
# In a real setup, the server would be the address of your Kafka cluster, but for local testing, we can use localhost.
server = 'localhost:9092'
topic_name = 'rides'

# Connect to Kafka as a consumer. auto_offset_reset='earliest' means we start reading from the beginning of the topic 
# (without this, new consumers default to latest and only see new messages).
# group_id identifies this consumer group - Kafka tracks how far each group has read, so restarting with the same group ID continues where it left off:
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[server],
    auto_offset_reset='earliest',
    group_id='rides-console',
    value_deserializer=ride_deserializer
)

print(f"Listening to {topic_name}...")

# Now we can pass ride_deserializer directly as the value_deserializer - Kafka calls it on every message, so message.value is already a Ride.
count = 0
for message in consumer:
    ride = message.value
    pickup_dt = datetime.fromtimestamp(ride.tpep_pickup_datetime / 1000)
    print(f"Received: PU={ride.PULocationID}, DO={ride.DOLocationID}, "
          f"distance={ride.trip_distance}, amount=${ride.total_amount:.2f}, "
          f"pickup={pickup_dt}")
    count += 1
    if count >= 10:
        print(f"\n... received {count} messages so far (stopping after 10 for demo)")
        break

consumer.close()