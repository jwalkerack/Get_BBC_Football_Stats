REPOSITORY OVERVIEW
-------------------
This repository is **1 of 4** in an end-to-end data pipeline that extracts, processes, and stores BBC data.

It focuses on **data extraction and preprocessing**, using:
- Python for web scraping and data transformation
- AWS Lambda for serverless execution
- Amazon S3 for cloud storage

Extracted data is stored in **JSON format** in an S3 bucket, with entity management controlled via a master JSON file.

DIRECTORY STRUCTURE
-------------------
LAMBDA_FUNCTION/
- Contains Python scripts for:
  - Data extraction (web scraping)
  - Data transformation (structuring & formatting)
  - S3 interaction (storing & retrieving data)
- Includes `app.py` and dependency files for AWS Lambda deployment.

StepsActionByUser/
- Contains scripts for **manual actions and testing**.
- Key scripts:
  - `Scenerio_Actions.py` → Defines user actions.
  - `FLOOD_S3.py` → Triggers data rebuilds (controlled for DEV or PRD).
  - `Return_One_Match_Save_To_File.py` → Saves a single game model for testing.

SUMMARY
-------
- Extracts and prepares raw BBC data for processing.
- Stores data in JSON format on Amazon S3.
- Automates workflows using AWS Lambda.
- Provides user-driven scripts for data validation and testing.

Next Part of the Process is Snowflake set up with repo
Stored here https://github.com/jwalkerack/snow_setup_football