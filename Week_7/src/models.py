import json
from dataclasses import dataclass

# Define a Ride dataclass to represent the structure of our ride data. This makes it easier to work with the data as Python objects instead of raw dictionaries.
@dataclass
class Ride:
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float
    tpep_pickup_datetime: int  # epoch milliseconds

# We first convert the Ride to a dictionary, then to a JSON string, and finally encode it to bytes.

# Serializer function to convert a Ride object to bytes for Kafka. 
def ride_from_row(row):
    return Ride(
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        trip_distance=float(row['trip_distance']),
        total_amount=float(row['total_amount']),
        tpep_pickup_datetime=int(row['tpep_pickup_datetime'].timestamp() * 1000),
    )

# Serializer function to convert a Ride object to bytes for Kafka.
def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)