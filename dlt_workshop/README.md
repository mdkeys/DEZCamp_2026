Notes for self for dlt-first-pipeline:

Prereqs:
- use "python3" instead of "python"

Workshop Instructions: I had to deactivate to stop using uv that was directed to my hw-wk1 directory. I then did the following to open virtual environment in my dlt_workshop folder to work out of. 
```
deactivate #exit uv
cd dlt_workshop/ #or name of directly
python3 -m venv .venv #set up venv
source .venv/bin/activate #set up venv
pip3 install "dlt[workspace]" #start dlt workspace
python3 -m dlt init dlthub:open_library duckdb #set up dlthub:open_library setup
```

Notes:
- Step 3: Used `pip3 install "dlt[workspace]"` instead of `pip`
- Step 4: need to use `python3 -m dlt init dlthub:open_library duckdb`
  - At this step, enter 'copilot' for the type of IDE assistant that is being used. (I assume it's copilot that's a part of the VS Code). When prompted to initiatlize pipeline 'open_library_pipeline.py' to add copilot rules/snippers, type 'Y' to proceed. 
  - This adds the open_library_pipeline.py and open_library-docs.yaml to the "dlt_workshop" folder you're working out of. It also added a .gitignore, and .dlt and .github folders with additional files. The files in .github/instructions are guidelines for the AI to use to prevent hallucinations and improve performance. 
  - The open_library-docs.yaml file will be used for the LLM (it's meant for the LLM to read so it is not as human-readable. you don't need to open it.)
- Step 5:
  - When following the video, we use the text:
    ```
    Please generate a REST API Source for Open Library API, as specified in @open_library-docs.yaml
    Use the search api and query harry potter books.
    Place the code in open_library_pipeline.py and name the pipeline open_library_pipeline.
    If the file exists, use it as a starting point.
    Do not add or modify any other files.
    Use @dlt rest api as a tutorial.
    After adding the endpoints, allow the user to run the pipeline with python open_library_pipeline.py and await further instructions.
    ```
  - After open_library_pipeline.py complete, run in terminal using `uv run open_library_pipeline.py`. If you get an error, give it to Copilot to fix and then re-run (this worked). In terminal, the confirmation is: `Pipeline open_library_pipeline load step completed in 0.36 seconds
  1 load package(s) were loaded to destination duckdb and into dataset open_library_data
  The duckdb destination used duckdb:////Users/mishadavies/src/DEZCamp_2026/dlt_workshop/open_library_pipeline.duckdb location to store data
  Load package 1772156100.52184 is LOADED and contains no failed jobs`
- Step 6: run `uv run dlt pipeline open_library_pipeline show` to set up a dashboard to inspect your data and metadata. This will show up in a browser. You can query the data in "Dataset Browser: Data and Source/Resource State". "Last Pipeline Run Trace" shows you how long each ELT step took if you want to diagnose any issues. 
- Step 8: Using the chat to inspect: I ran into some issues here. To figure out how many tables are in open_library_pipeline, the code that ended up working was `python3 check_tables.py` after it created a check_tables.py file. 
  - Note: I got 117 books in Spanish, not 164 like the video example. 

Explore your data with Marimo: 
- Lots of errors here. Eventually it opens in a notebook but I had to paste in the code to get it to work (whereas the workshop demo the code was already in the notebook). My output list was similar but not exactly the same numbers or author order as the demo example. 
- To turn the notebook into a report, type in terminal `uv run marimo run open_library_dashboard.py` (or in my case, `top_authors_marimo.py`) [I didn't test this]

**Homework**

```
deactivate #exit uv
cd dlt_workshop/ #or name of directly
python3 -m venv .venv #set up venv
source .venv/bin/activate #set up venv
pip3 install "dlt[workspace]" #start dlt workspace
python3 -m dlt init dlthub:taxi_pipeline duckdb #set up dlthub:taxi_pipeline setup
```

** NOTE ** The Copilot chat was NOT working. I put the instructions into my Claude AI and it was able to write the pipeline correctly on the first try. 

After putting in prompt and having taxi_pipeline.py set up, run with `uv run taxi_pipeline.py`

Now go to dlt dashboard: `uv run dlt pipeline taxi_pipeline show`

Queries:
#1: 2009-06-01 to 2009-07-01
```
SELECT
  MIN(trip_pickup_date_time) as start,
  MAX(trip_dropoff_date_time) as end
FROM "rides"
```
#2:
``` 0.2666
SELECT
SUM(case when payment_type = 'Credit' then 1 else 0 end) / count(*)
FROM "rides"
LIMIT 1000
```

#3: 6,063.41
```
SELECT
  ROUND(SUM(tip_amt), 2) AS total_tips
FROM "rides"
```