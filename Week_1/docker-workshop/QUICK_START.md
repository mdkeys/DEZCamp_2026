# Docker Pipeline Quick Start Guide

## Prerequisites
- Docker Desktop must be running
- You must be in the pipeline directory

## Step-by-Step Instructions

### 1. Navigate to Pipeline Directory
```bash
cd ~/src/DEZCamp_2026/Week_1/docker-workshop/pipeline
```

### 2. Start Database Services
```bash
docker compose up
```
**What you'll see:** Messages indicating PostgreSQL and pgAdmin are starting. Wait for "database system is ready to accept connections"

**Keep this terminal running** (or use `docker compose up -d` for detached mode)

### 3. Build Ingestion Image (First Time Only)
Open a **new terminal** and run:
```bash
cd ~/src/DEZCamp_2026/Week_1/docker-workshop/pipeline
docker build -t taxi_ingest .
```
**Note:** Only rebuild if you change Dockerfile or ingest_data.py

### 4. Run Data Ingestion
```bash
docker run -it \
  --network pipeline_default \
  taxi_ingest \
  --pg-host pgdatabase \
  --pg-user root \
  --pg-pass root \
  --pg-db ny_taxi \
  --pg-port 5432 \
  --year 2021 \
  --month 1 \
  --target-table yellow_taxi_data
```

**To ingest different months:** Change `--year` and `--month` parameters

### 5. Access pgAdmin
1. Open browser: http://localhost:8085
2. Login: admin@admin.com / root
3. Add server:
   - Name: Local Docker
   - Host: pgdatabase
   - Port: 5432
   - Username: root
   - Password: root
   - Database: ny_taxi

### 6. Stop Services
In the terminal running `docker compose up`, press:
```bash
Ctrl + C
```

Or if running in detached mode:
```bash
docker compose down
```

## Common Commands

```bash
# Check running containers
docker ps

# View logs
docker logs pipeline-pgdatabase-1

# Stop and remove all data (fresh start)
docker compose down -v

# Restart services
docker compose up
```

## Troubleshooting

**Database connection refused during ingestion:**
- Ensure `docker compose up` is running
- Use `--pg-host pgdatabase` (NOT localhost)
- Include `--network pipeline_default`

**No data in pgAdmin:**
- Verify you ran the ingestion step (step 4)
- Check ingestion logs for errors

**Docker command not found:**
- Ensure Docker Desktop is running
- Use `docker compose` (with space), not `docker-compose`
