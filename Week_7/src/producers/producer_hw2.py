# For HW #2 

import json
import sys
import time
from pathlib import Path

import pandas as pd
from kafka import KafkaProducer

url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"
columns = ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 
           'passenger_count', 'trip_distance', 'tip_amount', 'total_amount']

df = pd.read_parquet(url, columns=columns)

print(df[columns].isnull().sum())

def ride_serializer(row_dict):
    return json.dumps(row_dict).encode('utf-8')

server = 'localhost:9092'
topic_name = 'green-trips'

producer = KafkaProducer(
    bootstrap_servers=[server],
    value_serializer=ride_serializer
)

t0 = time.time()

for _, row in df.iterrows():
    row_dict = row.to_dict()
    # Convert datetime columns to strings
    row_dict['lpep_pickup_datetime'] = str(row['lpep_pickup_datetime'])
    row_dict['lpep_dropoff_datetime'] = str(row['lpep_dropoff_datetime'])
    producer.send(topic_name, value=row_dict)
    print(f"Sent: {row_dict}")

producer.flush()

t1 = time.time()
print(f'took {(t1 - t0):.2f} seconds')