# Using for homework question #3...

import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from kafka import KafkaProducer

# From models_hw.py, we import the Ride dataclass and the ride_from_row function which converts a dataframe row to a Ride object.
from models_hw import Ride, ride_from_row

# Download NYC green taxi trip data
url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"
columns = ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 'passenger_count', 'trip_distance', 'tip_amount', 'total_amount']
df = pd.read_parquet(url, columns=columns)

# ride serializer converts a Ride object to bytes for Kafka. It first converts the Ride to a dictionary, then to a JSON string, and finally encodes it to bytes.
def ride_serializer(ride):
    ride_dict = dataclasses.asdict(ride)
    json_str = json.dumps(ride_dict)
    return json_str.encode('utf-8')

server = 'localhost:9092'

producer = KafkaProducer(
    bootstrap_servers=[server],
    value_serializer=ride_serializer
)
t0 = time.time()

topic_name = 'green-trips3' # Was 'rides' in the workshop

# For each row in the dataframe, we convert it to a Ride object using ride_from_row (in models_hw.py), then send it to Kafka. 
# We also print out sent # rows for every 1000 rows
for i, (_, row) in enumerate(df.iterrows()):
    ride = ride_from_row(row)
    producer.send(topic_name, value=ride)
    if i % 1000 == 0:
        print(f"Sent {i} rows...")
    time.sleep(0.01)

producer.flush()

t1 = time.time()
print(f'took {(t1 - t0):.2f} seconds')