# Mod 5 - Bruin

**A few notes**
* I did Mod4 in dbt cloud & BigQuery, so I started Mod 5 by adjusting the examples to load data into BigQuery. I'm trying to save space on my laptop.
* I do not feel comfortable setting up the MCP in VS Code so I have deliberately skipped that step and the subsequent project to have it done. But I get it, it's very cool. I might do it later if I feel more comfortable with that type of AI integration. I just don't right now.
* Since Bruin cloud is an optional way to see and run the pipeline, I have also decided to skip that for this week.

## Q1: Requires files/directories for a Bruin pipeline structure:
- .bruin.yml
- pipeline.yml
- assets (can be anywhere). In the my-first-pipeline example, they are in the assets folder within the project. In the zoomcamp example, they are in a pipeline/assets folder. But the pipeline.yml does NOT need to be in a pipeline folder. 
- ANSWER: Option #2

## Q2: Materialization strategy - pipeline processes taxi data by month based on pickup_datetime. Which mat strategy to use in the staging layer that deduplicates and cleans the data?
- ANSWER: time_inveral (see zoomcamp/pipeline/assets/staging/trips.sql for example)
  
## Q3: How to override a pipeline variable (e.g., ["yellow","green"] but only run "yellow")?
- https://getbruin.com/docs/bruin/getting-started/pipeline-variables.html#overriding-variables
- ANSWER: bruin run --var 'taxi_types=["yellow"]'

## Q4: How to run asset with all downstream assets:
- ANSWER: bruin run --downstream	

## Q5: Quality checks to ensure column never has NULL values
- ANSWER: not_null: true (in code: -name: not_null)

## Q6: How to see dependency graph between assets?
- ANSWER: bruin lineage

## Q7: First time run. How to ensure tables are created from scratch?
- ANSWER: --full-refresh