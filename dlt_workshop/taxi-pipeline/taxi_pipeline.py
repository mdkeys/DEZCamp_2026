"""REST API source for NYC Taxi data using dlt."""

import dlt
import requests


@dlt.resource(write_disposition="replace")
def taxi_data():
    """Fetch NYC taxi data with pagination."""
    base_url = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"
    offset = 0
    limit = 1000
    
    while True:
        response = requests.get(base_url, params={"offset": offset}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Stop when we get an empty page
        if not data:
            break
            
        yield data
        offset += limit


@dlt.source
def taxi_pipeline():
    """Define dlt source for NYC Taxi data."""
    return taxi_data()


if __name__ == "__main__":
    print("Starting pipeline...")  # noqa: T201
    
    pipeline = dlt.pipeline(
        pipeline_name='taxi_pipeline',
        destination='duckdb',
        dataset_name='nyc_taxi_data'
    )
    
    print("Running pipeline...")  # noqa: T201
    load_info = pipeline.run(taxi_pipeline())
    
    print("Pipeline completed!")  # noqa: T201
    print(load_info)  # noqa: T201
