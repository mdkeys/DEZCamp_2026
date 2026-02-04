# Added comments to help with understanding. 

import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden
import time

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

# Change this to your bucket name (must be globally unique!)
BUCKET_NAME = "kestra-sandbox-485519-hw3" 

# AUTHENTICATION: How Python proves it has permission to access your GCS bucket

## Option 1: Use a service account JSON key file (recommended for scripts)
# If you authenticated through the GCP SDK you can comment out these two lines:
#CREDENTIALS_FILE = "DEZCAMP_2026/Week_2/keys/service-account.json"
#client = storage.Client.from_service_account_json(CREDENTIALS_FILE)

## Option 2: If you're already logged in via `gcloud auth login`, comment out 
# lines above and use this instead:
client = storage.Client(project='kestra-sandbox-485519') 

# Base URL for downloading NYC taxi data (CloudFront CDN)
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-"

# List of months to download: ['01', '02', '03', '04', '05', '06']
# The f"{i:02d}" formats numbers with leading zeros (1 becomes '01')
MONTHS = [f"{i:02d}" for i in range(1, 7)]

# Directory where files will be downloaded temporarily (current directory)
DOWNLOAD_DIR = "."

# Size of chunks when uploading to GCS (8 MB)
# Larger chunks = faster upload but more memory usage
CHUNK_SIZE = 8 * 1024 * 1024    # 8 MB in bytes

# Create the download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Create a bucket object that represents your GCS bucket
bucket = client.bucket(BUCKET_NAME)

# ============================================================================
# DOWNLOAD FUNCTION
# ============================================================================
"""
    Downloads a single Parquet file from the NYC taxi data source.
    Args:
        month: String like '01', '02', etc.
    Returns:
        file_path: Path to the downloaded file, or None if download failed
 """

def download_file(month):
    # Construct the full URL (e.g., ...yellow_tripdata_2024-01.parquet)
    url = f"{BASE_URL}{month}.parquet"
    # Construct the local file path where it will be saved
    file_path = os.path.join(DOWNLOAD_DIR, f"yellow_tripdata_2024-{month}.parquet")

    try:
        print(f"Downloading {url}...")
        # Download the file from the URL and save it locally
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

# ============================================================================
# BUCKET CREATION/VERIFICATION FUNCTION
# ============================================================================
"""
    Checks if a bucket exists and belongs to your project.
    Creates it if it doesn't exist.
    Exits if the bucket name is taken by someone else.
"""
def create_bucket(bucket_name):
    try:
        # Get bucket details
        bucket = client.get_bucket(bucket_name)

        # Check if the bucket belongs to the current project (does it belong to YOUR 
        # project or someone else's?)
        project_bucket_ids = [bckt.id for bckt in client.list_buckets()]
        if bucket_name in project_bucket_ids:
            print(
                f"Bucket '{bucket_name}' exists and belongs to your project. Proceeding..."
            )
        else:
            # If bucket exists but belongs to another GCP project
            print(
                f"A bucket with the name '{bucket_name}' already exists, but it does not belong to your project."
            )
            sys.exit(1) # Exit the program with error code

    except NotFound:
        # If the bucket doesn't exist, create it
        bucket = client.create_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")
    except Forbidden:
        # If the request is forbidden, it means the bucket exists but you don't have access to see details
        print(
            f"A bucket with the name '{bucket_name}' exists, but it is not accessible. Bucket name is taken. Please try a different bucket name."
        )
        sys.exit(1) # Exit the program with error code

# ============================================================================
# VERIFICATION FUNCTION
# ============================================================================
"""
    Checks if a file (blob) exists in the GCS bucket.
    A "blob" is GCS terminology for a file stored in a bucket.
    Args:
        blob_name: Name of the file in the bucket
    Returns:
        True if file exists, False otherwise
"""
def verify_gcs_upload(blob_name):
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)

# ============================================================================
# UPLOAD FUNCTION
# ============================================================================
"""
    Uploads a local file to Google Cloud Storage with retry logic.
    Args:
        file_path: Path to the local file to upload
        max_retries: Number of times to retry if upload fails
"""
def upload_to_gcs(file_path, max_retries=3):
    # Get just the filename (e.g., 'yellow_tripdata_2024-01.parquet')
    blob_name = os.path.basename(file_path)
    # Create a blob (file) object in the bucket
    blob = bucket.blob(blob_name)
    # Set the upload chunk size (how much data to upload at once)
    blob.chunk_size = CHUNK_SIZE

    # Ensure the bucket exists before uploading
    create_bucket(BUCKET_NAME)

    # Retry loop: try uploading up to max_retries times
    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            # Upload the file from local disk to GCS
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            # Verify the file actually made it to GCS
            if verify_gcs_upload(blob_name):
                print(f"Verification successful for {blob_name}")
                return  # Success! Exit the function
            else:
                print(f"Verification failed for {blob_name}, retrying...")
        except Exception as e:
            print(f"Failed to upload {file_path} to GCS: {e}")
        
        # Wait 5 seconds before retrying
        time.sleep(5)

    # If we get here, all retries failed
    print(f"Giving up on {file_path} after {max_retries} attempts.")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    # First, ensure the bucket exists
    create_bucket(BUCKET_NAME)

    # STEP 1: Download all files in parallel (4 at a time)
    # ThreadPoolExecutor runs multiple downloads simultaneously for speed
    with ThreadPoolExecutor(max_workers=4) as executor:
        # executor.map applies download_file to each month in MONTHS
        file_paths = list(executor.map(download_file, MONTHS))

    # STEP 2: Upload all downloaded files to GCS in parallel (4 at a time)
    # filter(None, file_paths) removes any None values (failed downloads)
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(upload_to_gcs, filter(None, file_paths))  # Remove None values

    print("All files processed and verified.")
