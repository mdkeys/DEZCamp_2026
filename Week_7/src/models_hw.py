import json
from dataclasses import dataclass
import pandas as pd

# Define a Ride dataclass to represent the structure of our ride data. This makes it easier to work with the data as Python objects instead of raw dictionaries.
@dataclass
class Ride:
    lpep_pickup_datetime: int  # epoch milliseconds
    lpep_dropoff_datetime: int  # epoch milliseconds
    PULocationID: int
    DOLocationID: int
    passenger_count: int
    trip_distance: float
    tip_amount: float
    total_amount: float

# We first convert the Ride to a dictionary, then to a JSON string, and finally encode it to bytes.

# Serializer function to convert a Ride object to bytes for Kafka. 
def ride_from_row(row):
    return Ride(
        #lpep_pickup_datetime=int(row['lpep_pickup_datetime'].timestamp() * 1000), # Convert to epoch milliseconds
        #lpep_dropoff_datetime=int(row['lpep_dropoff_datetime'].timestamp() *1000), # Convert to epoch milliseconds
        lpep_pickup_datetime=str(row['lpep_pickup_datetime']), # Keep as string for later Flink processing
        lpep_dropoff_datetime=str(row['lpep_dropoff_datetime']), # Keep as string for later Flink processing
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        passenger_count=int(row['passenger_count']) if pd.notna(row['passenger_count']) else 0, # Handle missing passenger_count by setting it to 0
        trip_distance=float(row['trip_distance']),
        tip_amount=float(row['tip_amount']),
        total_amount=float(row['total_amount']),
    )

# Serializer function to convert a Ride object to bytes for Kafka.
def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)