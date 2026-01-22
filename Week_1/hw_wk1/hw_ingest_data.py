#!/usr/bin/env python
# coding: utf-8

"""
Data ingestion script for NYC Green Taxi and Zone lookup data.
Loads parquet and CSV files into PostgreSQL database.
"""

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click
import ssl
import urllib.request


# Define data types for green taxi data
DTYPE_GREEN = {
    'VendorID': 'Int64',
    'passenger_count': 'Int64',
    'trip_distance': 'float64',
    'RatecodeID': 'Int64',
    'store_and_fwd_flag': 'string',
    'PULocationID': 'Int64',
    'DOLocationID': 'Int64',
    'payment_type': 'Int64',
    'fare_amount': 'float64',
    'extra': 'float64',
    'mta_tax': 'float64',
    'tip_amount': 'float64',
    'tolls_amount': 'float64',
    'improvement_surcharge': 'float64',
    'total_amount': 'float64',
    'trip_type': 'Int64',
    'congestion_surcharge': 'float64'
}

# Define data types for zones data
DTYPE_ZONES = {
    'LocationID': 'Int64',
    'Borough': 'string',
    'Zone': 'string',
    'service_zone': 'string'
}


def setup_ssl_context():
    """
    Set up SSL context to allow unverified HTTPS connections.
    This is needed for downloading from some sources with certificate issues.
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    print("SSL verification disabled for downloads")


def ingest_green_taxi_data(df_green, engine, table_name='green_tripdata', chunksize=100000):
    """
    Ingest green taxi parquet data into PostgreSQL in chunks.
    
    Args:
        df_green: DataFrame containing green taxi data
        engine: SQLAlchemy database engine
        table_name: Name of the target table
        chunksize: Number of rows to insert per chunk
    """
    print(f"\n{'='*50}")
    print(f"Ingesting {len(df_green)} rows to {table_name}")
    print(f"{'='*50}")
    
    # Create table structure (empty table with correct schema)
    df_green.head(0).to_sql(name=table_name, con=engine, if_exists="replace")
    print(f"Table {table_name} created")
    
    # Insert data in chunks
    total_rows = len(df_green)
    for i in tqdm(range(0, total_rows, chunksize), desc="Inserting chunks"):
        chunk = df_green.iloc[i:i + chunksize]
        chunk.to_sql(name=table_name, con=engine, if_exists="append")
    
    print(f'Done ingesting to {table_name}')


def ingest_zones_data(df_zones, engine, table_name='taxi_zones'):
    """
    Ingest zones CSV data into PostgreSQL.
    
    Args:
        df_zones: DataFrame containing zones data
        engine: SQLAlchemy database engine
        table_name: Name of the target table
    """
    print(f"\n{'='*50}")
    print(f"Ingesting {len(df_zones)} rows to {table_name}")
    print(f"{'='*50}")
    
    # Insert all zones data (small dataset, no chunking needed)
    df_zones.to_sql(name=table_name, con=engine, if_exists="replace")
    print(f'Done ingesting to {table_name}')


@click.command()
@click.option('--user', default='root', help='PostgreSQL username')
@click.option('--password', default='root', help='PostgreSQL password')
@click.option('--host', default='localhost', help='PostgreSQL host')
@click.option('--port', default='5432', help='PostgreSQL port')
@click.option('--db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--url-green', required=True, help='URL or path to green taxi parquet file')
@click.option('--url-zones', required=True, help='URL or path to zones CSV file')
@click.option('--table-green', default='green_tripdata', help='Green taxi table name')
@click.option('--table-zones', default='taxi_zones', help='Zones table name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for ingestion')
@click.option('--disable-ssl-verify', is_flag=True, default=False, help='Disable SSL certificate verification')
def main(user, password, host, port, db, url_green, url_zones, table_green, table_zones, chunksize, disable_ssl_verify):
    """
    Main function to orchestrate data ingestion for NYC Green Taxi and Zones data.
    """
    
    # Set up SSL context if needed
    if disable_ssl_verify:
        setup_ssl_context()
    
    print(f"\n{'='*50}")
    print("NYC Taxi Data Ingestion")
    print(f"{'='*50}")
    print(f"Host: {host}:{port}")
    print(f"Database: {db}")
    print(f"User: {user}")
    
    # Create database engine
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    print("Database connection established")
    
    # Read and process green taxi data
    print(f"\n{'='*50}")
    print(f"Reading green taxi data from: {url_green}")
    print(f"{'='*50}")
    
    try:
        df_green = pd.read_parquet(url_green)
        print(f"Loaded {len(df_green)} rows, {len(df_green.columns)} columns")
    except Exception as e:
        print(f"Error reading parquet file: {e}")
        raise
    
    # Apply data types
    df_green = df_green.astype(DTYPE_GREEN)
    print("Data types applied")
    
    # Display schema info
    print("\nGreen Taxi Data Schema:")
    print(pd.io.sql.get_schema(df_green, name=table_green, con=engine))
    
    # Read and process zones data
    print(f"\n{'='*50}")
    print(f"Reading zones data from: {url_zones}")
    print(f"{'='*50}")
    
    try:
        df_zones = pd.read_csv(url_zones)
        print(f"Loaded {len(df_zones)} rows, {len(df_zones.columns)} columns")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise
    
    # Apply data types
    df_zones = df_zones.astype(DTYPE_ZONES)
    print("Data types applied")
    
    # Display schema info
    print("\nZones Data Schema:")
    print(pd.io.sql.get_schema(df_zones, name=table_zones, con=engine))
    
    # Ingest green taxi data
    ingest_green_taxi_data(df_green, engine, table_green, chunksize)
    
    # Ingest zones data
    ingest_zones_data(df_zones, engine, table_zones)
    
    print(f"\n{'='*50}")
    print("All data ingestion complete!")
    print(f"{'='*50}")
    print(f"Tables created:")
    print(f"  - {table_green}")
    print(f"  - {table_zones}")


if __name__ == '__main__':
    main()