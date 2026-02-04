## Setup Instructions
Notes:
- I decided to use Docker so that I did not have to install packages onto my local environment.
- My working directory is Week_3/hw_wk3.
- I reused my kestra-sandbox project in GCP from Module 2 in order to keep all datafiles in one place under my kestra-sandbox-485519 project. 

1. Save load_yellow_taxi_data.py from https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/03-data-warehouse/load_yellow_taxi_data.py. 
2. Create a Dockerfile to create a container to run Python in. Use uv to download packages. 
    - Note: `--system` applies to the container since it's being created in the container, not your local environment. 
3. Login to GCP. There are several ways to do this and this took me the longest time to do, especially because I decided to re-use my kestra-sandbox project so I had to eventually redirect to a DIFFERENT folder for my credentials. 
   1. In terminal, type `gcloud auth login`. This will open a browser for you to log into GCP with your google account. After this is complete, the terminal will say 
   ```You are now logged in as [your email address]. Your current project is [None]. You can change this setting by running: $gcloud config set project PROJECT_ID```
   2. In terminal, I tried to configure the project to be my kestra-sandbox-485519 project by running `gcloud config set project kestra-sandbox-485519`. This raised a message in the terminal that there is a different Application Default Credential (ADC) associated with my account, which might cause some issues. I could have tried to set the ADC to this by running `gcloud auth application-default set-quota-project kestra-sandbox-485519` but I did not do that. Instead, I just moved on.
4. In load_yellow_taxi_data.py:
   1. Changed the BUCKET_NAME to a unique name: `BUCKET_NAME = "kestra-sandbox-485519-hw3"`. 
   2. Updated the credentials code to redirect it to my desired project: `client = storage.Client(project='kestra-sandbox-485519')`.  
5. Build the docker image. Run in terminal: `docker build -t yellow-taxi-uploader .`
6. Start a new container from the image. Note that the following -v works to access my credentials from my Week_2 folder: 
```
docker run \ 
-v ../../Week_2/keys/service-account.json:/app/gcs.json:ro \ 
-e GOOGLE_APPLICATION_CREDENTIALS=/app/gcs.json \
yellow-taxi-uploader
```
  - After running this, it took about a minute before terminal showed that the files were being downloaded and uploaded to my project folder in GCP.
7. Go to GCP in your brower & confirm you're in kestra-sandbox project. On the left-hand side, find "Cloud Storage" > "Buckets". You should see the "kestra-sandbox-485519-hw3" bucket. 
   1. Click the bucket to confirm your 6 datafiles are present.
8. Go to BigQuery studio and start a new SQL query. You will NOT see your datafiles listed because they are in the GCS bucket, not in BQ.
9. See DEZC_Mod3_hw3.sql for queries and answers to questions. 
10. Don't forget to close down your containers & images when you're done. 