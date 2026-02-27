"""REST API source for NYC Taxi data using dlt.

Loads paginated NYC Yellow Taxi trip data into DuckDB.

API details:
- Base URL: https://us-central1-dlthub-analytics.cloudfunctions.net
- Endpoint: /data_engineering_zoomcamp_api
- Pagination: page numbers (?page=1, ?page=2, ...), 1000 records per page
- Stop condition: empty page returned
"""

import dlt
from dlt.sources.rest_api import rest_api_source


def taxi_source():
    """Define the REST API source for NYC taxi data."""
    return rest_api_source({
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net",
        },
        "resource_defaults": {
            "write_disposition": "replace",
        },
        "resources": [
            {
                "name": "rides",
                "endpoint": {
                    "path": "data_engineering_zoomcamp_api",
                    "paginator": {
                        "type": "page_number",
                        "base_page": 1,
                        "page_param": "page",
                        "total_path": None,
                        "stop_after_empty_page": True,
                    },
                },
            },
        ],
    })


if __name__ == "__main__":
    # Create the pipeline
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="nyc_taxi_data",
        progress="log",
    )

    # Run the full pipeline: Extract → Normalize → Load
    load_info = pipeline.run(taxi_source())
    print(load_info)