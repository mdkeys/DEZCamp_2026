import dlt
from dlt.sources.rest_api import rest_api_source

# Define the Open Library API REST source
open_library_source = rest_api_source({
    "client": {
        "base_url": "https://openlibrary.org",
    },
    "resource_defaults": {
        "primary_key": "key",
        "write_disposition": "replace",
        "endpoint": {
            "params": {
                "limit": 50
            }
        }
    },
    "resources": [
        {
            "name": "books",
            "endpoint": {
                "path": "/search.json",
                "method": "GET",
                "params": {
                    "title": "harry potter",
                    "limit": 50,
                },
                "data_selector": "docs[*]",
                "paginator": {
                    "type": "offset",
                    "offset": 0,
                    "limit": 50,
                    "total_path": "numFound"
                }
            }
        }
    ]
})

# Define and run the pipeline
if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="open_library_pipeline",
        destination="duckdb",
        dataset_name="open_library_data"
    )
    
    load_info = pipeline.run(
        open_library_source
    )
    
    print(load_info)