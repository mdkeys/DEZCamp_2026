# Week 1 Homework
What I accomplished:
- Created data ingestion script (hw_ingest_data.py)
- Set up Docker containers for PostgreSQL and pgAdmin
- Loaded green taxi and zones data into PostgreSQL (had to remove SSL verify)
- Completed SQL queries in pgAdmin

## To run tomorrow:
1. Start Docker: `docker compose up -d`
2. Access pgAdmin: http://localhost:8085 (admin@admin.com / root)
3. Run ingestion: `uv run python hw_ingest_data.py --host=localhost --url-green=... --url-zones=... --disable-ssl-verify`

## Notes:
- Remember to use double quotes for column names in SQL: "PULocationID"
- Use single quotes for string values: 'Newark Airport'
- SSL verification needs to be disabled for cloudfront URLs
