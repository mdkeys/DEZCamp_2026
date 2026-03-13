import json
from kafka import KafkaConsumer

server = 'localhost:9092'
topic_name = 'green-trips'

def ride_deserializer(data):
    return json.loads(data.decode('utf-8'))

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[server],
    auto_offset_reset='earliest',
    group_id='green-trips-counter',
    value_deserializer=ride_deserializer,
    consumer_timeout_ms=5000  # stops after 5 seconds of no new messages
)

print(f"Listening to {topic_name}...")

total_count = 0
over_5km_count = 0

for message in consumer:
    ride = message.value
    total_count += 1
    if ride['trip_distance'] > 5.0:
        over_5km_count += 1
    if total_count % 1000 == 0:
        print(f"Processed {total_count} rows...")

consumer.close()

print(f"\nTotal trips: {total_count}")
print(f"Trips with trip_distance > 5km: {over_5km_count}")