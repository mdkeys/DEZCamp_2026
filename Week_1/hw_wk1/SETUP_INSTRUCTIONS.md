# NYC Taxi Data Ingestion - Complete Setup Guide

This guide will walk you through setting up and running the NYC Green Taxi data ingestion pipeline from scratch.

**NOTE** you will have two options at steps 4 & 5 to either run the setup as:
- **A: Fully Dockerized** 
  - Python and PostgreSQL run in Docker containers
  - Everything is isolated from the host machine
- **B: Not fully Dockerized**
  - Python runs on host machine in a virtual environment managed by uv
  - Connects to PostgreSQL running in Docker

---

## 📋 Prerequisites

Before starting, make sure you have:
- Docker Desktop installed and running
- Python 3.9+ installed
- VS Code (or any terminal)
- Internet connection for downloading data

---

## 🚀 Step-by-Step Instructions

### Step 1: Open Terminal in VS Code

1. Open VS Code
2. Open the folder containing these files (Dockerfile, docker-compose.yaml, hw_ingest_data.py)
3. Open a new terminal: **Terminal → New Terminal** (or press `` Ctrl+` ``)
4. Verify you're in the correct directory: 
```bash
ls
```
   
You should see: `Dockerfile`, `docker-compose.yaml`, `hw_ingest_data.py`

**What this does:** Ensures you're in the right location before running commands.

---

### Step 2: Start Docker Desktop

1. Open Docker Desktop application
2. Wait until you see "Docker Desktop is running" (green indicator)

**What this does:** Docker needs to be running to create and manage containers.

**⚠️ CRITICAL:** You MUST complete this step before Step 3. Docker must be running before you can start containers.

---

### Step 3: Start the Database Containers

Run this command in your terminal: 
```bash 
docker compose up -d
```

**What this does:**
- Creates and starts two Docker containers:
  1. **PostgreSQL database** (pgdatabase) - stores your data
  2. **pgAdmin** (web interface) - lets you view and query the data
- The `-d` flag runs them in the background (detached mode)
- Data will be stored in Docker volumes so it persists even if you stop the containers

**Expected output:**
```
✔ Network hw_wk1_default                    Created
✔ Volume hw_wk1_pgadmin_data                Created
✔ Volume hw_wk1_ny_taxi_postgres_data       Created
✔ Container hw_wk1-pgdatabase-1             Started
✔ Container hw_wk1-pgadmin-1                Started
```

**Verify it worked:**
```bash
docker ps
```
You should see two containers running: one with `postgres:18` and one with `pgadmin4`.

**⚠️ CRITICAL:** You MUST complete this step before Step 5. The database must be running before you can load data into it.

---
## **At this point you can follow instruction Setup A (Docker) or B (host machine) to carry out the remaining steps**

**Benefits of Docker approach (Setup A)**
- ✅ No Python installation needed on host machine
- ✅ Reproducible everywhere - same image works on any computer with Docker
- ✅ Production-ready - this is how it would be deployed
- ✅ Isolated - doesn't touch your system Python
- ✅ Uses your existing Dockerfile - the one you already have

## Setup A: Using Docker

### Step 4A: Build the Data Ingestion Docker Image

Run this command to build your Docker image:

```bash
docker build -t hw-ingest:v001 .
```

**What this does:**
- Reads the `Dockerfile` and builds a custom Docker image
- Installs Python 3.13 and `uv` package manager
- Installs all required packages (pandas, sqlalchemy, psycopg2-binary, tqdm, click)
- Copies your `hw_ingest_data.py` script into the image
- Tags the image as `hw-ingest:v001` so you can reference it later

**Expected output (will be similar but not exact):**
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [1/6] FROM python:3.13.10-slim
 => CACHED [2/6] COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
 => [3/6] WORKDIR /app
 => [4/6] COPY pyproject.toml uv.lock .python-version ./
 => [5/6] RUN uv sync --locked
 => [6/6] COPY hw_ingest_data.py hw_ingest_data.py
 => exporting to image
 => naming to docker.io/library/hw-ingest:v001
```

**This will take 1-3 minutes** the first time (downloads Python image and installs packages).

**Verify the image was created:**
```bash
docker images | grep hw-ingest
```
You should see: `hw-ingest   v001`

**⚠️ CRITICAL:** You MUST complete this step before Step 5. The ingestion container needs this image to run.

---

### Step 5A: Run the Data Ingestion Container

First, find your Docker network name:

```bash
docker network ls
```

Look for a network with your folder name (e.g., `hw_wk1_default`).

Now run the ingestion container (replace `hw_wk1_default` with your actual network name if different):

```bash
docker run -it --rm \
  --network=hw_wk1_default \
  hw-ingest:v001 \
  --user=root \
  --password=root \
  --host=pgdatabase \
  --port=5432 \
  --db=ny_taxi \
  --url-green=https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet \
  --url-zones=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv \
  --table-green=green_tripdata \
  --table-zones=taxi_zones \
  --chunksize=50000 \
  --disable-ssl-verify
```

**What this does:**
- Creates a temporary container from your `hw-ingest:v001` image
- Runs the ingestion script inside the container
- Downloads NYC Green Taxi data from November 2025 (parquet file, ~47k rows)
- Downloads NYC Taxi Zone lookup data (CSV file, 265 rows)
- Converts data to proper formats (integers, strings, dates)
- Loads data into PostgreSQL in chunks (50,000 rows at a time)
- Creates two tables: `green_tripdata` and `taxi_zones`
- Container automatically removes itself after completion

**What each parameter means:**
- `--network=hw_wk1_default` - Connects container to same network as PostgreSQL
- `hw-ingest:v001` - The Docker image to run
- `--user=root` / `--password=root` - Database login credentials
- `--host=pgdatabase` - PostgreSQL container name (NOT localhost - we're inside Docker!)
- `--port=5432` - PostgreSQL internal port (NOT 5433 - we're inside Docker network!)
- `--db=ny_taxi` - Database name where data will be stored
- `--url-green` - URL to download green taxi trip data
- `--url-zones` - URL to download zone lookup data
- `--table-green` - Name for the green taxi table in database
- `--table-zones` - Name for the zones table in database
- `--chunksize=50000` - Load 50k rows at a time (prevents memory issues)
- `--disable-ssl-verify` - Allows download from sources with SSL certificate issues

**Key differences from running on host (Set B instructions):**
- `--host=pgdatabase` instead of `--host=localhost` (uses Docker service name)
- `--port=5432` instead of `--port=5433` (uses internal Docker port)

**Expected output:**
```
==================================================
NYC Taxi Data Ingestion
==================================================
Host: pgdatabase:5432
Database: ny_taxi
User: root
Database connection established

==================================================
Reading green taxi data from: https://...
==================================================
Loaded 46912 rows, 21 columns
Data types applied

Green Taxi Data Schema:
CREATE TABLE green_tripdata (
    ...
)

==================================================
Ingesting 46912 rows to green_tripdata
==================================================
Inserting chunks: 100%|██████████| 1/1 [00:15<00:00, 15.32s/it]
Done ingesting to green_tripdata

==================================================
Ingesting 265 rows to taxi_zones
==================================================
Done ingesting to taxi_zones

==================================================
All data ingestion complete!
==================================================
Tables created:
  - green_tripdata
  - taxi_zones
```

**This will take 2-5 minutes** depending on your internet speed.

---
## Setup B: Using Host Machine: (Skip to Step 6 if you've already followed Setup A steps 4 & 5)

### Step 4B: Install Python Dependencies
Run this command to install required Python packages:

**(if using uv):**
`uv add pandas sqlalchemy psycopg2-binary tqdm click`

**What this does:**
- `uv add` - Uses UV python package manager to add the following packages to python using a Python virtual environment (.venv)
- `pandas` - reads and processes data files
- `sqlalchemy` - connects Python to PostgreSQL
- `psycopg2-binary` - PostgreSQL driver for Python
- `tqdm` - shows progress bars during data loading
- `click` - handles command-line arguments

**Alternative (if using uv):**
`pip install pandas sqlalchemy psycopg2-binary tqdm click`


**⚠️ CRITICAL:** You MUST complete this step before Step 5. Python needs these libraries to run the ingestion script.

---

### Step 5B: Run the Data Ingestion Script

Copy and paste this entire command into your terminal:

`uv run python hw_ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5433 \
  --db=ny_taxi \
  --url-green=https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet \
  --url-zones=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv \
  --table-green=green_tripdata \
  --table-zones=taxi_zones \
  --chunksize=50000 \
  --disable-ssl-verify`

**What this does:**
- Downloads NYC Green Taxi data from November 2025 (parquet file, ~47k rows)
- Downloads NYC Taxi Zone lookup data (CSV file, 265 rows)
- Converts data to proper formats (integers, strings, dates)
- Loads data into PostgreSQL in chunks (50,000 rows at a time)
- Creates two tables: `green_tripdata` and `taxi_zones`

**What each parameter means:**
- `uv run python hw_ingest_data.py \` - Uses uv (Python package manager/installer) to run the hw_ingest_data.py file using python
- `--user=root` / `--password=root` - Database login credentials
- `--host=localhost` - Connect to database on your local machine
- `--port=5433` - PostgreSQL is accessible on port 5433 (see docker-compose.yaml)
- `--db=ny_taxi` - Database name where data will be stored
- `--url-green` - URL to download green taxi trip data
- `--url-zones` - URL to download zone lookup data
- `--table-green` - Name for the green taxi table in database
- `--table-zones` - Name for the zones table in database
- `--chunksize=50000` - Load 50k rows at a time (prevents memory issues)
- `--disable-ssl-verify` - Allows download from sources with SSL certificate issues

**Expected output:**
```
==================================================
NYC Taxi Data Ingestion
==================================================
Host: localhost:5433
Database: ny_taxi
User: root
Database connection established

==================================================
Reading green taxi data from: https://...
==================================================
Loaded 46912 rows, 21 columns
Data types applied
...
[Progress bars showing data insertion]
...
==================================================
All data ingestion complete!
==================================================
Tables created:
  - green_tripdata
  - taxi_zones
```

**This will take 2-5 minutes** depending on your internet speed.

---

### Step 6: Access pgAdmin to View Your Data

1. Open your web browser
2. Go to: **http://localhost:8085**
3. Login with:
   - **Email:** `admin@admin.com`
   - **Password:** `root`

**What this does:** Opens the pgAdmin web interface where you can view and query your data.

---

### Step 7: Connect to the Database in pgAdmin (First Time Only)

Once logged into pgAdmin:

1. **Right-click "Servers"** in the left sidebar
2. Select **Register → Server**

3. **General tab:**
   - Name: `NYC Taxi Database` (or any name you like)

4. **Connection tab:**
   - Host name/address: `pgdatabase`
   - Port: `5432`
   - Maintenance database: `ny_taxi` **(Why isn't it `postgres`?)**
   - Username: `root`
   - Password: `root`
   - ✅ Check "Save password"

5. Click **Save**

**What this does:** Creates a connection from pgAdmin to your PostgreSQL database.

**Why `pgdatabase` and not `localhost`?**
- pgAdmin runs inside Docker, so it uses the Docker service name (`pgdatabase`)
- When you ran the ingestion script, you used `localhost` because it ran outside Docker

---

### Step 8: View Your Data

In pgAdmin's left sidebar, navigate to:

```
Servers → NYC Taxi Database → Databases → ny_taxi → Schemas → public → Tables
```

You should see two tables:
- **green_tripdata** (46,912 rows)
- **taxi_zones** (265 rows)

**To view data:**
- Right-click on a table → **View/Edit Data → All Rows**

**To run SQL queries:**
- Right-click on `ny_taxi` database → **Query Tool**
- Try this query:
  ```sql
  SELECT COUNT(*) FROM green_tripdata;
  ```

---

## ✅ Verification Checklist

Confirm everything worked:

- [ ] Docker Desktop is running
- [ ] Two containers are running (`docker ps` shows pgdatabase and pgadmin)
- [ ] (Setup A) Docker image built successfully (`docker images | grep hw-ingest`)
- [ ] Python script completed without errors
- [ ] pgAdmin opens at http://localhost:8085
- [ ] Database connection successful in pgAdmin
- [ ] Two tables visible: `green_tripdata` and `taxi_zones`
- [ ] Query `SELECT COUNT(*) FROM green_tripdata;` returns 46,912

---

## 🔄 Order of Operations (Dependencies)

**MUST follow this order:**

1. **Docker Desktop running** ← Required before Step 3
2. **Start containers** (`docker compose up -d`) ← Required before Step 5
3. **Setup A**
   1. **Build ingestion image** (`docker build`) ← Required before Step 5
   2. **Run ingestion container** (`docker run`) ← Creates tables needed for Step 8
4. **Setup B**
   1. **Install Python packages** ← Required before Step 5
   2. **Run ingestion script** ← Creates tables needed for Step 8
5. **Access pgAdmin** ← Can be done anytime after Step 3
6. **Connect to database in pgAdmin** ← Required to view data

**What happens if you skip steps?**
- Skip Step 2 → Step 3 fails with "Docker daemon not running"
- Skip Step 3 → Step 5 fails with "connection refused" (no database to connect to)
- Skip Step 4 → Step 5 fails with "ModuleNotFoundError" (missing Python packages)
- Skip Step 5 → Step 8 shows no tables (data wasn't loaded)

---

## 🔁 Running Again (After Initial Setup A)

If you need to re-run the ingestion (e.g., to reload data):

```bash
# Start containers if they're not running
docker compose up -d

# Run ingestion again (image already built, so skip that step)
docker run -it \
  --network=hw_wk1_default \
  hw-ingest:v001 \
  --user=root \
  --password=root \
  --host=pgdatabase \
  --port=5432 \
  --db=ny_taxi \
  --url-green=https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet \
  --url-zones=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv \
  --table-green=green_tripdata \
  --table-zones=taxi_zones \
  --chunksize=50000 \
  --disable-ssl-verify
```

**Note:** You only need to rebuild the image (`docker build`) if you change:
- `hw_ingest_data.py` script
- `pyproject.toml` dependencies
- `Dockerfile` itself

---

## 🛑 Stopping Everything 

When you're done working (Both Setups A & B):

# Stop containers (keeps your data)
`docker compose down`

# Stop and delete all data
`docker compose down -v`

**Important:** Using `-v` flag deletes your database data permanently!

## 🧹 Cleanup (Remove Everything) (Setup A)

To completely clean up (remove containers, images, volumes):

```bash
# Stop containers and remove volumes
docker compose down -v

# Remove the ingestion image
docker rmi hw-ingest:v001

# Verify everything is gone
docker ps -a
docker images
docker volume ls

# If images aren't gone, run this with the image ID(s) following the command:
docker rmi 
```

---

## 🆘 Troubleshooting **NOTE: Troubleshooting section has not been reviewed for accuracy**

### Error: "Docker daemon not running"

**Solution:** Start Docker Desktop and wait for it to fully start.

### Error: "network hw_wk1_default not found"

**Solution:** The network name might be different.

```bash
# Find the actual network name
docker network ls

# Use the network that contains your folder name
# Example: if you see "my_project_default", use that
```

### Error: "could not translate host name 'pgdatabase'"

**Solution:** You're not on the Docker network.

Make sure you include `--network=hw_wk1_default` in your `docker run` command.

### Error: "connection refused" when running ingestion

**Solution:** Database isn't running or not ready.

```bash
# Check containers are running
docker ps

# If not running, start them
docker compose up -d

# Wait 10-15 seconds for PostgreSQL to fully initialize
sleep 15

# Then try the ingestion again
```

### Error: "image not found: hw-ingest:v001"

**Solution:** You didn't build the image.

```bash
docker build -t hw-ingest:v001 .
```

### Error: "SSL certificate verify failed"

**Solution:** You forgot the `--disable-ssl-verify` flag.

Re-run the command from Step 5 with that flag included.

### Can't see tables in pgAdmin

**Solutions:**
1. Make sure ingestion container ran successfully (check Step 5 output)
2. Refresh pgAdmin: Right-click on `ny_taxi` → Refresh
3. Check you're looking in: Databases → ny_taxi → Schemas → public → Tables
4. Make sure you connected to `pgdatabase:5432` not `localhost:5433`

### Error: "column 'PULocationID' does not exist" in SQL queries

**Solution:** PostgreSQL column names are case-sensitive when created by pandas.

Use double quotes around column names:
```sql
-- Correct ✓
SELECT "PULocationID" FROM green_tripdata LIMIT 5;

-- Wrong ✗
SELECT PULocationID FROM green_tripdata LIMIT 5;
```

### Ingestion script runs but no data appears

**Solution:** Check if the script actually completed.

Look for this at the end of the output:
```
All data ingestion complete!
Tables created:
  - green_tripdata
  - taxi_zones
```

If you see errors instead, read the error message and check network/database connectivity.

### Error: "Port 5433 already in use"

**Solution:** Another application is using port 5433.

```bash
# Find what's using the port
lsof -i :5433

# Kill the process (replace PID with actual number from above)
kill <PID>

# Or change the port in docker-compose.yaml to 5434
```

### Error: "ModuleNotFoundError: No module named 'pandas'"

**Solution:** Python packages aren't installed.

```bash
pip install pandas sqlalchemy psycopg2-binary tqdm click
```

---

## 📚 Next Steps

Now that your data is loaded, you can:

1. **Run SQL queries** in pgAdmin's Query Tool
2. **Analyze taxi trips** by location, time, fare amounts
3. **Join tables** to see zone names instead of just IDs:
   ```sql
   SELECT 
       g."PULocationID",
       z."Zone",
       z."Borough",
       COUNT(*) as trip_count
   FROM green_tripdata g
   JOIN taxi_zones z ON g."PULocationID" = z."LocationID"
   GROUP BY g."PULocationID", z."Zone", z."Borough"
   ORDER BY trip_count DESC
   LIMIT 10;
   ```
4. **See README.md** for SQL queries used for the homework. 

---

## 💡 Docker vs Host Machine: Key Concepts

### When running on host machine (with uv):
- Uses: `--host=localhost --port=5433`
- Why: Connecting from outside Docker to Docker's exposed port
- Python: Runs on your computer

### When running in Docker (this guide):
- Uses: `--host=pgdatabase --port=5432`
- Why: Connecting from inside Docker network using service names
- Python: Runs inside a container

Both approaches work! Docker is more portable and production-ready.

---